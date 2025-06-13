from app.models.storage_type import StorageType
from tests.utils.asserts import assert_dict_contains
from app.models import StorageElement, HardwareItem


def test_create_storage_element(client, db_session):
    new_storage_item = {
        "name": "Elektrik",
        "location": "Basement",
        "position": "L0",
        "storage_type_id": 2,
        "description": "Contains electronic tools",
    }

    response = client.post("/api/storage/", json=new_storage_item)
    assert response.status_code == 200, response.content

    data = response.json()
    print(data)
    assert data["id"] == 3
    assert data["location"] == "Basement"
    assert data["position"] == "L0"
    assert data["storage_type_id"] == 2
    assert data["description"] == "Contains electronic tools"
    assert data["storage_type"]["name"] == "Box"

    item = db_session.get(StorageElement, 3)
    assert data["location"] == item.location
    assert data["position"] == item.position
    assert data["storage_type_id"] == item.storage_type_id
    assert data["description"] == item.description

    item = db_session.get(StorageType, 2)
    assert data["storage_type"]["name"] == item.name


def test_list_storage_elements(client):
    response = client.get("/api/storage/")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2  # adjust if your seed has more/less
    items = data["items"]
    assert len(items) == 2

    assert_dict_contains(
        "validating storage element attributes",
        {
            "id": 1,
            "name": "WD 1",
            "location": "Basement/White",
            "position": "1",
            "storage_type_id": 1,
            "description": "White Drawer number 1",
            "storage_type": {
                "id": 1,
                "name": "Gridfinity Tray",
                "printing_strategy": "Gridfinity",
                "description": "A samla tray of gridfinity",
            },
        },
        items[0],
    )


def test_list_storage_elements_with_offset_and_limit(client):
    response = client.get("/api/storage/", params={"offset": 1, "limit": 1})
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 1

    assert_dict_contains(
        "validating second storage element returned with offset",
        {
            "id": 2,
            "name": "Cabel Tray",
        },
        data["items"][0],
        [
            "root['location']",
            "root['position']",
            "root['storage_type_id']",
            "root['description']",
            "root['storage_type']",
        ],
    )


def test_get_storage_element_by_id(client):
    response = client.get("/api/storage/", params={"id": 1})
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["id"] == 1


def test_update_storage_element(client, db_session):
    update = {
        "name": "Updated Drawer",
        "location": "Attic",
        "position": "99",
        "storage_type_id": 2,
        "description": "Updated description",
    }
    response = client.put("/api/storage/1", json=update)
    assert response.status_code == 200

    element = db_session.get(StorageElement, 1)
    for key, value in update.items():
        assert getattr(element, key) == value


def test_delete_storage_element(client):
    response = client.delete("/api/storage/2")
    assert response.status_code == 200

    response = client.get("/api/storage/")
    data = response.json()
    assert data["total"] == 1
    assert all(element["id"] != 2 for element in data["items"])


def test_mark_all_for_printing(client, db_session):

    # prepare
    item = db_session.get(HardwareItem, 1)
    item.queued_for_printing = False
    db_session.commit()

    # check if all is set to False
    items = (
        db_session.query(HardwareItem)
        .join(StorageElement)
        .filter(StorageElement.id == 1)
        .all()
    )
    assert any(not item.queued_for_printing for item in items)

    response = client.post("/api/storage/markallforprinting/1")
    assert 200 == response.status_code

    # now check everything is set to true
    items = (
        db_session.query(HardwareItem)
        .join(StorageElement)
        .filter(StorageElement.id == 1)
        .all()
    )
    assert any(item.queued_for_printing for item in items)
