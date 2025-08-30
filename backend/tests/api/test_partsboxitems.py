from unittest.mock import patch

from app.models.partsbox_item import PartsboxItem
from tests.utils.asserts import assert_dict_contains
from tests.utils.partsbox import mock_partsbox_data


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_items(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data

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
            "id": "04q14a3fv04f6a8f5s1g68p0mf",
            "name": "808-AG10D",
            "material_part_number": "808-AG10D",
            "description": "8 Position 2 Row 7.62 mm (Row Spacing) 2.54 mm Pitch Through Hole Dip Socket",
            "total_stock": 2,
            "storage_place": "PartBox 1 (Black)",
        },
        first_item,
        exclude_paths=[],
    )


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_page(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data

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
            "id": "063tfs8qa0jkc8berhdkswwv4m",
            "name": "MT3608L Boost Converter",
            "description": "Boost Converter (2.5A, <=20V LCSC: C2832326) (M36)",
            "total_stock": 18,
            "storage_place": "Gridfinity ICs",
            "material_part_number": "MT3608L",
        },
        first_item,
        exclude_paths=[],
    )


@patch("app.domain.partsbox.partsbox_service.requests.get")
def test_list_partsbox_sort(mock_get, mock_partsbox_data, client):
    """Test Listing of Partsbox Items"""
    mock_get.side_effect = mock_partsbox_data

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

    list_response = client.get("/api/electronic-parts/", params={"filters": "name:YSP"})
    data = list_response.json()
    print(data)

    assert list_response.status_code == 200
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert any(i["name"] == "YSPI1050-470M" for i in data["items"])
    assert any(i["name"] == "YSPI0740-220M" for i in data["items"])

    mock_get.side_effect = mock_partsbox_data
    list_response = client.get(
        "/api/electronic-parts/", params={"filters": ["name:resistor", "name:1k"]}
    )
    data = list_response.json()
    print(data)

    assert data["total"] == 2
    assert len(data["items"]) == 2

    mock_get.side_effect = mock_partsbox_data
    list_response = client.get(
        "/api/electronic-parts/",
        params={"filters": ["name:resistor", "storage_place:Part Box 2 (black)"]},
    )
    data = list_response.json()
    print(data)

    assert data["total"] == 30
    assert len(data["items"]) == 10
    assert all(
        "resistor" in i["name"].lower() and i["storage_place"] == "Part Box 2 (black)"
        for i in data["items"]
    )
