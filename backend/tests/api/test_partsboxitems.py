from unittest.mock import patch

from app.models.partsbox_item import PartsboxItem
from app.domain.partsbox.partsbox_service import PartsboxService
from tests.utils.asserts import assert_dict_contains
from tests.utils.partsbox import mock_partsbox_data


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_items(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._reset()

    list_response = client.get("/api/electronic-parts/")
    data = list_response.json()
    print(data)

    assert list_response.status_code == 200
    assert data["total"] == 188
    assert len(data["items"]) == 10  # Default page size is 10

    first_item = data["items"][0]
    assert isinstance(first_item, dict)
    assert_dict_contains(
        "checking created hardware item values",
        {
            "id": "51kng3zb58jwh9p4wwsv5rpnge",
            "name": '0.9" OLED (I2C)',
            "material_part_number": "",
            "description": '0.9" (4 Lines) OLED with I2C connector',
            "total_stock": 4,
            "storage_place": "White-Drawer-2",
            "queued_for_printing": False,
            "label": "",
        },
        first_item,
        exclude_paths=[],
    )


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_page(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._reset()

    list_response = client.get(
        "/api/electronic-parts/", params={"limit": 2, "offset": 1}
    )
    data = list_response.json()
    print(data)

    assert list_response.status_code == 200
    assert data["total"] == 188
    assert len(data["items"]) == 2

    first_item = data["items"][0]
    assert isinstance(first_item, dict)
    assert_dict_contains(
        "checking created hardware item values",
        {
            "id": "e0t4wm3ftr4f6a8f5s1g68p0mf",
            "name": "001",
            "description": "Antennas for 433 MHz radio receivers/transmitters",
            "total_stock": 10,
            "storage_place": "Parts Sorting Cupbard (blue)",
            "material_part_number": "",
            "queued_for_printing": False,
            "label": "",
        },
        first_item,
        exclude_paths=[],
    )


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_sort(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._reset()

    list_response = client.get("/api/electronic-parts/", params={"sort_by": "name"})
    data = list_response.json()
    print(data)

    assert list_response.status_code == 200
    assert data["total"] == 188
    assert len(data["items"]) == 10  # Default page size is 10
    assert data["items"][0]["name"] == '0.9" OLED (I2C)'

    mock_get.side_effect = mock_partsbox_data
    list_response = client.get(
        "/api/electronic-parts/", params={"sort_by": "name", "asc": "false"}
    )
    data = list_response.json()
    print(data)
    assert data["total"] == 188
    assert len(data["items"]) == 10  # Default page size is 10
    assert data["items"][0]["name"] == "ZX-QC34-2TPDZ"


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_filter(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._reset()

    list_response = client.get("/api/electronic-parts/", params={"filter": "name:YSP"})
    data = list_response.json()
    print(data)

    assert list_response.status_code == 200
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert any(i["name"] == "YSPI1050-470M" for i in data["items"])
    assert any(i["name"] == "YSPI0740-220M" for i in data["items"])

    mock_get.side_effect = mock_partsbox_data
    list_response = client.get(
        "/api/electronic-parts/", params={"filter": ["name:resistor", "name:1k"]}
    )
    data = list_response.json()
    print(data)

    assert data["total"] == 2
    assert len(data["items"]) == 2

    mock_get.side_effect = mock_partsbox_data
    list_response = client.get(
        "/api/electronic-parts/",
        params={"filter": ["name:resistor", "storage_place:Part Box 2 (black)"]},
    )
    data = list_response.json()
    print(data)

    assert data["total"] == 30
    assert len(data["items"]) == 10
    assert all(
        "resistor" in i["name"].lower() and i["storage_place"] == "Part Box 2 (black)"
        for i in data["items"]
    )


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_queued(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items with queued for printing status"""
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._reset()

    PartsboxService.fetch_parts()
    PartsboxService.queue_for_printing("71cp5tyrrmjweaw6mwy6tezfks")

    list_response = client.get("/api/electronic-parts/", params={"filter": "name:YSP"})
    data = list_response.json()
    print(data)

    assert list_response.status_code == 200
    assert data["total"] == 2
    assert data["items"][1]["queued_for_printing"]
    assert not data["items"][0]["queued_for_printing"]


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_queue_partbox_item_for_printing(mock_get, mock_partsbox_data, client):
    """Test queueing a Partsbox item for printing"""
    mock_get.side_effect = mock_partsbox_data
    PartsboxService._reset()

    list_response = client.get(
        "/api/electronic-parts/queueforprinting/71cp5tyrrmjweaw6mwy6tezfks"
    )
    data = list_response.json()
    assert list_response.status_code == 200
    assert "71cp5tyrrmjweaw6mwy6tezfks queued for label printing" in data["message"]
    assert PartsboxService.is_queued_for_printing("71cp5tyrrmjweaw6mwy6tezfks")

    list_response = client.get(
        "/api/electronic-parts/unqueueforprinting/71cp5tyrrmjweaw6mwy6tezfks"
    )
    data = list_response.json()
    assert list_response.status_code == 200
    assert "71cp5tyrrmjweaw6mwy6tezfks unqueued for label printing" in data["message"]
    assert not PartsboxService.is_queued_for_printing("71cp5tyrrmjweaw6mwy6tezfks")
