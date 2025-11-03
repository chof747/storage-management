import json
from pytest import fixture
from unittest.mock import MagicMock
from pathlib import Path


@fixture
def mock_partsbox_data():
    parts_file = Path(__file__).parent.parent / "resources" / "partsbox_parts_all.json"
    storage_file = (
        Path(__file__).parent.parent / "resources" / "partsbox_storage_all.json"
    )

    with parts_file.open() as f:
        parts_data = json.load(f)

    with storage_file.open() as f:
        storage_data = json.load(f)

    # Mock the API responses
    parts_response_mock = MagicMock()
    parts_response_mock.json.return_value = parts_data
    parts_response_mock.raise_for_status = MagicMock()

    storage_response_mock = MagicMock()
    storage_response_mock.json.return_value = storage_data
    storage_response_mock.raise_for_status = MagicMock()
    return [parts_response_mock, storage_response_mock]
