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
