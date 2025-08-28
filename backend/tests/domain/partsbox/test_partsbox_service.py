import time
import pytest
from unittest.mock import patch, MagicMock
from app.domain.partsbox.partsbox_service import PartsboxService
from app.models.partsbox_item import PartsboxItem
import json
from pathlib import Path


@pytest.fixture
def mock_partsbox_data():
    parts_file = (
        Path(__file__).parent.parent.parent / "resources" / "partsbox_parts_all.json"
    )
    storage_file = (
        Path(__file__).parent.parent.parent / "resources" / "partsbox_storage_all.json"
    )

    with parts_file.open() as f:
        parts_data = json.load(f)

    with storage_file.open() as f:
        storage_data = json.load(f)

    return parts_data, storage_data


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_fetch_parts_more_than_one(mock_get, mock_partsbox_data):
    parts_data, storage_data = mock_partsbox_data

    # Mock the API responses
    parts_response_mock = MagicMock()
    parts_response_mock.json.return_value = parts_data
    parts_response_mock.raise_for_status = MagicMock()

    storage_response_mock = MagicMock()
    storage_response_mock.json.return_value = storage_data
    storage_response_mock.raise_for_status = MagicMock()

    mock_get.side_effect = [parts_response_mock, storage_response_mock]

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
    parts_data, storage_data = mock_partsbox_data

    # Mock the API responses
    parts_response_mock = MagicMock()
    parts_response_mock.json.return_value = parts_data
    parts_response_mock.raise_for_status = MagicMock()

    storage_response_mock = MagicMock()
    storage_response_mock.json.return_value = storage_data
    storage_response_mock.raise_for_status = MagicMock()

    mock_get.side_effect = [parts_response_mock, storage_response_mock]
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
    mock_get.side_effect = [parts_response_mock, storage_response_mock]

    parts_third_call = PartsboxService.fetch_parts()
    assert mock_get.call_count == 4
    assert parts_third_call == parts_first_call  # Data should be the same


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_get_parts_sorted_and_paginated(mock_get, mock_partsbox_data):
    parts_data, storage_data = mock_partsbox_data

    # Create a list of PartsboxItem instances with varying names and total_stock
    # Mock the API responses
    parts_response_mock = MagicMock()
    parts_response_mock.json.return_value = parts_data
    parts_response_mock.raise_for_status = MagicMock()

    storage_response_mock = MagicMock()
    storage_response_mock.json.return_value = storage_data
    storage_response_mock.raise_for_status = MagicMock()

    mock_get.side_effect = [parts_response_mock, storage_response_mock]
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
    parts_data, storage_data = mock_partsbox_data

    # Mock the API responses
    parts_response_mock = MagicMock()
    parts_response_mock.json.return_value = parts_data
    parts_response_mock.raise_for_status = MagicMock()

    storage_response_mock = MagicMock()
    storage_response_mock.json.return_value = storage_data
    storage_response_mock.raise_for_status = MagicMock()

    mock_get.side_effect = [parts_response_mock, storage_response_mock]
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
