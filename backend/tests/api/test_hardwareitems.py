from backend.tests.conftest import TestingSessionLocal
from tests.utils.asserts import assert_dict_contains


def test_create_hardware_items(client):
    """Test Creation of a Hardware Item"""

    new_hwitem = {
        "hwtype": "Screw",
        "main_metric": "M3",
        "secondary_metric": "BH",
        "length": 5.0,
        "storage_element_id": 1,
        "reorder": False,
    }

    create_response = client.post(
        "/api/items/",
        json=new_hwitem,
    )
    data = create_response.json()
    print(data)

    assert create_response.status_code == 200
    assert data["id"] == 3
    assert data["storage_element"]["id"] == 1

    assert_dict_contains(
        "checking created hardware item values",
        new_hwitem,
        data,
        exclude_paths=[
            "root['reorder_link']",
            "root['queued_for_printing']",
            "root['id']",
            "root['storage_element']",
        ],
    )


def test_list_hardware_items(client):

    list_response = client.get("/api/items/")
    assert list_response.status_code == 200
    response = list_response.json()

    n = response["total"]
    items = response["items"]
    assert n == 2

    assert_dict_contains(
        "asserting value of first returned hw item",
        {
            "id": 1,
            "hwtype": "Screws",
            "main_metric": "M3",
            "secondary_metric": "BH",
            "length": 5.0,
            "reorder": True,
            "reorder_link": "http://amazon.de",
            "storage_element_id": 1,
            "queued_for_printing": True,
        },
        items[0],
        exclude_paths="root['storage_element']",
    )

    assert_dict_contains(
        "asserting attributes of associated storage element for 1. hw item",
        {
            "id": 1,
            "name": "WD 1",
            "location": "Basement/White",
            "position": "1",
            "storage_type": "Gridfinity",
            "description": "White Drawer number 1",
        },
        items[0]["storage_element"],
    )


def test_list_hardware_items_with_offset_and_limit(client):

    list_response = client.get(
        "/api/items/",
        params={
            "offset": 1,
            "limit": 1,
        },
    )
    assert list_response.status_code == 200
    response = list_response.json()

    total = response["total"]
    items = response["items"]
    assert total == 2
    assert len(items) == 1

    assert_dict_contains(
        "asserting returned hw item is the second",
        {
            "id": 2,
            "hwtype": "Washer",
            "main_metric": "M3",
            "secondary_metric": "",
            "length": 0.5,
            "reorder": False,
            "reorder_link": None,
            "storage_element_id": 1,
            "queued_for_printing": False,
        },
        items[0],
        exclude_paths="root['storage_element']",
    )


def test_update_hwitem_value(client):
    new_values = {
        "hwtype": "Bolt",
        "main_metric": "M4",
        "length": 15.0,
        "reorder": False,
        "queued_for_printing": False,
    }
    response = client.put(
        "/api/items/1",
        json=new_values,
    )

    print(response.content)
    assert response.status_code == 200


def test_delete_hwitem(client):
    response = client.delete("/api/items/2")
    assert response.status_code == 200

    response = client.get("/api/items")
    data = response.json()
    total = data["total"]
    items = data["items"]
    assert total == 1
    assert not any(i["id"] == 2 for i in items)


def test_queue_and_unqueue_for_printing(client, db_session):
    response = client.get("/api/items/queueforprinting/2")
    assert response.status_code == 200

    from app.models.hardware_item import HardwareItem

    item = db_session.get(HardwareItem, 2)
    assert item.queued_for_printing
