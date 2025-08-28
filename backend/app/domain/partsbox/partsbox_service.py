import requests
import os
import time

from app.models.partsbox_item import PartsboxItem


class PartsboxService:

    BASE_URL = os.getenv("PARTSBOX_BASE_URL", "https://partsbox.com/api")
    API_KEY = os.getenv("PARTSBOX_API_KEY", "")
    STORAGE_PLACE_UNKNOWN = "Unknown"

    # Global cache
    _cache = {"data": None, "timestamp": 0}
    CACHE_EXPIRATION = int(os.getenv("PARTSBOX_CACHE_EXPIRATION", 3600))

    @classmethod
    def _validate_results(cls, r: dict) -> dict:
        # Check status for parts response
        if r.get("partsbox.status/category", "").upper() != "OK":
            raise Exception(r.get("partsbox.status/message", "Unknown error"))

        return r.get("data", None)

    @classmethod
    def fetch_parts(cls, refresh_cache: bool = False) -> list[PartsboxItem]:
        """
        Fetch all parts and storage data from the Partsbox.io API,
        then build and return a list of PartsboxItem instances.
        """
        current_time = time.time()

        if refresh_cache:
            cls._cache = {"data": None, "timestamp": 0}

        # Check if cache is still valid
        if cls._cache["data"] and (
            current_time - cls._cache["timestamp"] < cls.CACHE_EXPIRATION
        ):
            return cls._cache["data"]

        headers = {
            "Authorization": f"APIKey {PartsboxService.API_KEY}",
            "Content-Type": "application/json",
        }

        # Fetch all parts
        parts_response = requests.get(
            f"{PartsboxService.BASE_URL}/part/all", headers=headers
        )
        parts_response.raise_for_status()
        parts_data = cls._validate_results(parts_response.json())

        # Fetch all storage
        storage_response = requests.get(
            f"{PartsboxService.BASE_URL}/storage/all", headers=headers
        )
        storage_response.raise_for_status()
        storage_data = cls._validate_results(
            storage_response.json()
        )  # Assuming the API returns JSON

        # Build PartsboxItem instances
        partsbox_items = []
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
                    PartsboxService.STORAGE_PLACE_UNKNOWN,
                )
            else:
                storage_place = PartsboxService.STORAGE_PLACE_UNKNOWN

            partsbox_item = PartsboxItem(
                id=part["part/id"],
                name=part["part/name"],
                description=part["part/description"] or "",
                material_part_number=(part["part/mpn"] if "part/mpn" in part else ""),
                total_stock=total_stock,
                storage_place=storage_place,
            )
            partsbox_items.append(partsbox_item)

        # Update cache
        cls._cache["data"] = partsbox_items
        cls._cache["timestamp"] = current_time

        return partsbox_items

    @classmethod
    def sort(
        cls,
        parts: list[PartsboxItem],
        key: str = "name",
        ascending: bool = True,
    ) -> list[PartsboxItem]:
        """
        Sorts a list of PartsboxItem objects based on a specified attribute and order.
        Args:
            parts (list[PartsboxItem]): The list of PartsboxItem items to be sorted.
            key (str, optional): The attribute name to sort by. Defaults to "name".
            ascending (bool, optional): If True, sorts in ascending order; if False, sorts in descending order. Defaults to True.
        Returns:
            list[PartsboxItem]: The sorted list of PartsboxItem objects.
        Raises:
            ValueError: If the specified key is not a valid attribute of PartsboxItem.
        """

        # Sort parts
        try:
            parts.sort(key=lambda x: getattr(x, key), reverse=not ascending)
        except AttributeError:
            raise ValueError(f"Invalid sort_by attribute: {key}")

        return parts

    @classmethod
    def paginate(
        cls,
        parts: list[PartsboxItem],
        offset: int = 0,
        limit: int = 20,
    ) -> list[PartsboxItem]:
        """
        Paginates a list of PartsboxItem objects.
        Args:
            parts (list[PartsboxItem]): The list of PartsboxItem items to be paginated.
            offset (int, optional): The starting index of the items to retrieve. Defaults to 0.
            limit (int, optional): The maximum number of items to retrieve. Defaults to 20.
        Returns:
            list[PartsboxItem]: The paginated list of PartsboxItem objects for the specified range.
        Raises:
            ValueError: If the offset or limit is less than 0.
        """

        if offset < 0 or limit < 1:
            raise ValueError(
                "Offset must be non-negative and limit must be greater than 0."
            )

        return parts[offset : offset + limit]

    @classmethod
    def filter(
        cls, parts: list[PartsboxItem], field: str, filter_value: str
    ) -> list[PartsboxItem]:
        """
        Filters a list of PartsboxItem objects based on a specified field and filter value.
        Args:
            parts (list[PartsboxItem]): The list of PartsboxItem items to be filtered.
            field (str): The attribute name to filter by.
            filter_value (str): The value to filter the specified field by.
        Returns:
            list[PartsboxItem]: The filtered list of PartsboxItem objects.
        Raises:
            ValueError: If the specified field is not a valid attribute of PartsboxItem.
        """
        try:
            filtered_parts = [
                part
                for part in parts
                if filter_value.lower() in str(getattr(part, field)).lower()
            ]
        except AttributeError:
            raise ValueError(f"Invalid filter field: {field}")

        return filtered_parts
