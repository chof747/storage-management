import os
import time
import logging
from typing import Optional

import requests

from app.models.partsbox_item import PartsboxItem

LOG = logging.getLogger("partsbox_service")


class _PartsboxServiceImpl:
    """Instance implementation of the Partsbox service.

    This class holds state (cache, printing queue, session) and reads configuration
    when an instance is created. It's intended to be instantiated by callers who
    want isolated instances (e.g. in tests) or by the facade below which lazily
    creates a singleton instance.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        cache_expiration: Optional[int] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url or os.getenv(
            "PARTSBOX_BASE_URL", "https://partsbox.com/api"
        )
        self.api_key = api_key or os.getenv("PARTSBOX_API_KEY", "")
        self.STORAGE_PLACE_UNKNOWN = "Unknown"

        self._cache = {"data": None, "timestamp": 0}
        self._printing_queue: set[str] = set()
        self.CACHE_EXPIRATION = int(
            cache_expiration or os.getenv("PARTSBOX_CACHE_EXPIRATION", 3600)
        )

        # Allow injection of a requests-like session for easier testing
        self.session = session or requests

    def _validate_results(self, r: dict) -> dict:
        if r.get("partsbox.status/category", "").upper() != "OK":
            raise Exception(r.get("partsbox.status/message", "Unknown error"))
        return r.get("data", None)

    def _reset(self) -> None:
        self._cache = {"data": None, "timestamp": 0}
        self._printing_queue = set()

    def _get_header(self) -> dict:
        return {
            "Authorization": f"APIKey {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def clear_cache(self) -> None:
        self._reset()
        LOG.info("Partsbox cache cleared on request.")

    def fetch_parts(self, refresh_cache: bool = False) -> list[PartsboxItem]:
        """Fetch all parts and storage data from the Partsbox API and return a list of PartsboxItem."""
        current_time = time.time()

        if refresh_cache:
            self._reset()
            LOG.info("Refreshing Partsbox cache cleared for initialization.")

        if self._cache["data"] and (
            current_time - self._cache["timestamp"] < self.CACHE_EXPIRATION
        ):
            return self._cache["data"]

        # fetch
        headers = self._get_header()

        parts_response = self.session.get(self._build_url("/part/all"), headers=headers)
        parts_response.raise_for_status()
        parts_data = self._validate_results(parts_response.json())

        storage_response = self.session.get(
            self._build_url("/storage/all"), headers=headers
        )
        storage_response.raise_for_status()
        storage_data = self._validate_results(storage_response.json())

        LOG.info(
            f"Fetched {len(parts_data)} parts and {len(storage_data)} storage locations from Partsbox API."
        )

        partsbox_items: list[PartsboxItem] = []
        for part in parts_data:
            total_stock = sum(entry["stock/quantity"] for entry in part["part/stock"])
            if total_stock > 0 and part["part/stock"]:
                latest_stock = max(
                    part["part/stock"], key=lambda s: s["stock/timestamp"]
                )
                storage_place = next(
                    (
                        storage["storage/name"]
                        for storage in storage_data
                        if storage["storage/id"] == latest_stock["stock/storage-id"]
                    ),
                    self.STORAGE_PLACE_UNKNOWN,
                )
            else:
                storage_place = self.STORAGE_PLACE_UNKNOWN

            if (
                "part/cad-keys" in part.keys()
                and isinstance(part["part/cad-keys"], list)
                and len(part["part/cad-keys"]) > 0
            ):
                label = part["part/cad-keys"][0]
            else:
                label = ""

            partsbox_item = PartsboxItem(
                id=part["part/id"],
                name=part["part/name"],
                description=part["part/description"] or "",
                label=label,
                material_part_number=(part["part/mpn"] if "part/mpn" in part else ""),
                total_stock=total_stock,
                storage_place=storage_place,
            )
            partsbox_items.append(partsbox_item)

        # Update cache
        self._cache["data"] = partsbox_items
        self._cache["timestamp"] = current_time

        return partsbox_items

    def get_header(self) -> dict:
        return self._get_header()

    def sort(
        self, parts: list[PartsboxItem], key: str = "name", ascending: bool = True
    ) -> list[PartsboxItem]:
        try:
            parts.sort(key=lambda x: getattr(x, key), reverse=not ascending)
        except AttributeError:
            raise ValueError(f"Invalid sort_by attribute: {key}")
        return parts

    def paginate(
        self, parts: list[PartsboxItem], offset: int = 0, limit: int = 20
    ) -> list[PartsboxItem]:
        if offset < 0 or limit < 1:
            raise ValueError(
                "Offset must be non-negative and limit must be greater than 0."
            )
        return parts[offset : offset + limit]

    def filter(
        self, parts: list[PartsboxItem], field: str, filter_value: str
    ) -> list[PartsboxItem]:
        try:
            filtered_parts = [
                part
                for part in parts
                if filter_value.lower() in str(getattr(part, field)).lower()
            ]
        except AttributeError:
            raise ValueError(f"Invalid filter field: {field}")
        return filtered_parts

    def queue_for_printing(self, part_id: str) -> None:
        self._printing_queue.add(part_id)

    def unqueue_for_printing(self, part_id: str) -> None:
        self._printing_queue.discard(part_id)

    def is_queued_for_printing(self, part_id: str) -> bool:
        return part_id in self._printing_queue

    def queued_part_ids(self) -> set[str]:
        return self._printing_queue

    def update_part_label(self, part_id: str, new_label: str) -> bool:
        headers = self._get_header()
        payload = {
            "part/id": part_id,
            "part/cad-keys": [new_label] if new_label else [],
        }
        response = self.session.post(
            self._build_url("/part/update"), json=payload, headers=headers
        )
        if getattr(response, "status_code", None) == 200:
            LOG.info(f"Updated label for part {part_id} to '{new_label}'")
            return True
        else:
            LOG.error(
                f"Failed to update label for part {part_id}. Status code: {getattr(response, 'status_code', None)}, Response: {getattr(response, 'text', None)}"
            )
            return False


class PartsboxService:
    """Facade class to preserve the previous static/classmethod API while using an
    instance-based implementation under the hood. The implementation instance is
    created lazily on first use, so environment variables are read at that time
    (fixes import-time initialization issues).
    """

    _impl: Optional[_PartsboxServiceImpl] = None

    @classmethod
    def _get_impl(cls) -> _PartsboxServiceImpl:
        if cls._impl is None:
            cls._impl = _PartsboxServiceImpl()
        return cls._impl

    @classmethod
    def _reset(cls) -> None:
        """Compatibility wrapper to reset the underlying instance state (cache and queue)."""
        return cls._get_impl()._reset()

    # Facade / compatibility wrappers -------------------------------------------------
    @classmethod
    def clear_cache(cls) -> None:
        return cls._get_impl().clear_cache()

    @classmethod
    def fetch_parts(cls, refresh_cache: bool = False) -> list[PartsboxItem]:
        return cls._get_impl().fetch_parts(refresh_cache)

    @classmethod
    def get_header(cls) -> dict:
        return cls._get_impl().get_header()

    @classmethod
    def sort(
        cls, parts: list[PartsboxItem], key: str = "name", ascending: bool = True
    ) -> list[PartsboxItem]:
        return cls._get_impl().sort(parts, key=key, ascending=ascending)

    @classmethod
    def paginate(
        cls, parts: list[PartsboxItem], offset: int = 0, limit: int = 20
    ) -> list[PartsboxItem]:
        return cls._get_impl().paginate(parts, offset=offset, limit=limit)

    @classmethod
    def filter(
        cls, parts: list[PartsboxItem], field: str = "", filter_value: str = ""
    ) -> list[PartsboxItem]:
        return cls._get_impl().filter(parts, field, filter_value)

    @classmethod
    def queue_for_printing(cls, part_id: str) -> None:
        return cls._get_impl().queue_for_printing(part_id)

    @classmethod
    def unqueue_for_printing(cls, part_id: str) -> None:
        return cls._get_impl().unqueue_for_printing(part_id)

    @classmethod
    def is_queued_for_printing(cls, part_id: str) -> bool:
        return cls._get_impl().is_queued_for_printing(part_id)

    @classmethod
    def queued_part_ids(cls) -> set[str]:
        return cls._get_impl().queued_part_ids()

    @classmethod
    def update_part_label(cls, part_id: str, new_label: str) -> bool:
        return cls._get_impl().update_part_label(part_id, new_label)

    # Factory method for callers who want an explicit instance (recommended)
    @classmethod
    def create_instance(
        cls,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        cache_expiration: Optional[int] = None,
        session: Optional[requests.Session] = None,
    ) -> _PartsboxServiceImpl:
        return _PartsboxServiceImpl(
            base_url=base_url,
            api_key=api_key,
            cache_expiration=cache_expiration,
            session=session,
        )
