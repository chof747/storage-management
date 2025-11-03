import time
import pytest
from unittest.mock import patch
from app.domain.partsbox.partsbox_service import PartsboxService
from app.models.partsbox_item import PartsboxItem

from tests.utils.partsbox import mock_partsbox_data


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_fetch_parts_more_than_one(mock_get, mock_partsbox_data):
    PartsboxService._cache = {"data": None, "timestamp": 0}
    mock_get.side_effect = mock_partsbox_data

    # Call the fetch_parts method
    parts = PartsboxService.fetch_parts()

    # Assert that the number of parts fetched is more than 1
    assert len(parts) == 188
    assert isinstance(parts[0], PartsboxItem)
    assert parts[0].storage_place == "Gridfinity ICs"
    assert parts[0].total_stock == 18
    assert parts[0].id == "063tfs8qa0jkc8berhdkswwv4m"
    assert parts[0].name == "MT3608L Boost Converter"
    assert parts[0].material_part_number == "MT3608L"
    assert parts[0].label == "M36"
    assert parts[0].description == "Boost Converter (2.5A, <=20V LCSC: C2832326) (M36)"


@pytest.mark.integration
def test_fetch_parts_real_service():
    # Call the fetch_parts method to query the real service
    parts = PartsboxService.fetch_parts()

    # Assert that the number of parts fetched is more than 1
    assert len(parts) > 1
    assert isinstance(parts[0], PartsboxItem)

    # Optionally, check some attributes of the first item
    assert hasattr(parts[0], "id")
    assert hasattr(parts[0], "name")
    assert hasattr(parts[0], "total_stock")
    assert hasattr(parts[0], "storage_place")


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_fetch_parts_cache(mock_get, mock_partsbox_data):
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._cache = {"data": None, "timestamp": 0}

    # Call the fetch_parts method for the first time
    parts_first_call = PartsboxService.fetch_parts()

    # Assert that the API was called
    assert mock_get.call_count == 2

    # Call the fetch_parts method again (should use cache)
    parts_second_call = PartsboxService.fetch_parts()

    # Assert that the API was not called again
    assert mock_get.call_count == 2

    # Assert that the cached data is returned
    assert parts_first_call == parts_second_call

    # Simulate cache expiration by modifying the timestamp
    PartsboxService._cache["timestamp"] -= PartsboxService.CACHE_EXPIRATION + 1
    time.sleep(1)  # Ensure time has passed
    mock_get.side_effect = mock_partsbox_data

    parts_third_call = PartsboxService.fetch_parts()
    assert mock_get.call_count == 4
    assert parts_third_call == parts_first_call  # Data should be the same


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_get_parts_sorted_and_paginated(mock_get, mock_partsbox_data):

    mock_get.side_effect = mock_partsbox_data
    PartsboxService._cache = {"data": None, "timestamp": 0}

    # Call the fetch_parts method
    parts = PartsboxService.paginate(
        PartsboxService.sort(PartsboxService.fetch_parts(), key="name", ascending=True),
        offset=2,
        limit=10,
    )

    assert len(parts) == 10
    assert parts[0].name <= parts[1].name
    assert parts[0].name == "0467001.NR"

    parts = PartsboxService.paginate(
        PartsboxService.sort(
            PartsboxService.fetch_parts(), key="total_stock", ascending=False
        ),
        offset=0,
        limit=8,
    )

    print(parts[0])
    assert len(parts) == 8
    assert parts[0].total_stock >= parts[1].total_stock
    assert parts[0].total_stock == 257
    assert parts[7].total_stock == 199


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_filter_fetched_parts(mock_get, mock_partsbox_data):
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._cache = {"data": None, "timestamp": 0}

    # Call the fetch_parts method
    parts = PartsboxService.fetch_parts()

    filtered_parts = PartsboxService.filter(parts, "description", "10kOhm")

    assert len(filtered_parts) == 2
    assert all("10kOhm" in part.description for part in filtered_parts)
    assert any(part.id == "11w931wk9wh17b7j848fasrwh3" for part in filtered_parts)
    assert any(part.id == "2xs7yj3fxp4f6a8f5s1g68p0mf" for part in filtered_parts)

    filtered_parts = PartsboxService.filter(parts, "storage_place", "White-Drawer-2")
    assert len(filtered_parts) == 33
    assert all("White-Drawer-2" in part.storage_place for part in filtered_parts)


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_queue_for_printing(mock_get, mock_partsbox_data):
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._cache = {"data": None, "timestamp": 0}
    PartsboxService._printing_queue = set()

    # Call the fetch_parts method
    parts = PartsboxService.fetch_parts()

    part_to_queue = parts[0]
    PartsboxService.queue_for_printing(part_to_queue.id)
    assert part_to_queue.id in PartsboxService._printing_queue

    # Queue the same part again (should not duplicate)
    PartsboxService.queue_for_printing(part_to_queue.id)
    assert len(PartsboxService._printing_queue) == 1
    assert PartsboxService.is_queued_for_printing(part_to_queue.id)

    # Queue another part
    another_part = parts[1]
    PartsboxService.queue_for_printing(another_part.id)
    assert another_part.id in PartsboxService._printing_queue
    assert len(PartsboxService._printing_queue) == 2
    assert PartsboxService.is_queued_for_printing(another_part.id)

    # Check the queued parts
    queue = PartsboxService.queued_part_ids()
    for id in [part_to_queue.id, another_part.id]:
        assert any(qid == id for qid in queue)

    # Unqueue a part
    PartsboxService.unqueue_for_printing(part_to_queue.id)
    assert len(PartsboxService._printing_queue) == 1
    assert not PartsboxService.is_queued_for_printing(part_to_queue.id)
