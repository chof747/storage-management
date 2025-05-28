from app.models.storage_element import StorageElement
from tests.utils.asserts import assert_dict_contains
from app.models.storage_type import StorageType


def test_create_storage_type(client, db_session):
    new_type = {
        "name": "Crate",
        "description": "plastic storage crate",
        "printing_strategy": "Gridfinity",
    }
    response = client.post("/api/storagetype/", json=new_type)
    assert response.status_code == 200, response.content
    created = response.json()

    assert created["id"] > 0
    assert created["name"] == "Crate"
    assert created["description"] == "plastic storage crate"

    db_stype = db_session.get(StorageType, created["id"])
    assert db_stype is not None
    assert db_stype.name == "Crate"


def test_list_storage_types(client):
    response = client.get("/api/storagetype/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # adjust if more/less in CSV
    assert len(data["items"]) == 2

    assert_dict_contains(
        "checking attributes of first storage type",
        {
            "id": 1,
            "name": "Gridfinity Tray",
            "description": "A samla tray of gridfinity",
            "printing_strategy": "Gridfinity",
        },
        data["items"][0],
    )


def test_list_storage_types_with_offset_and_limit(client):
    response = client.get("/api/storagetype/", params={"offset": 1, "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1

    assert data["items"][0]["id"] == 2
    assert data["items"][0]["name"] == "Box"


def test_get_storage_type_by_id(client):
    response = client.get("/api/storagetype/", params={"id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == 1
    assert data["items"][0]["printing_strategy"] == "Gridfinity"


def test_update_storage_type(client, db_session):
    new_data = {
        "name": "Gridfinity Advanced",
        "description": "improved modular system",
    }

    response = client.put("/api/storagetype/1", json=new_data)
    assert response.status_code == 200, response.content

    stype = db_session.get(StorageType, 1)
    assert stype.name == "Gridfinity Advanced"
    assert stype.description == "improved modular system"


def test_printing_strategy_validation(client):
    new_data = {
        "printing_strategy": "whatever",
    }
    response = client.put("/api/storagetype/1", json=new_data)
    assert response.status_code == 422, response.content
    details = response.json()["detail"]

    assert len(details) == 1
    assert details[0]["type"] == "value_error"
    assert details[0]["loc"] == ["body", "printing_strategy"]
    assert "Value error, Invalid label printer specified: whatever" in details[0]["msg"]


def test_delete_storage_type_with_violation(client):
    response = client.delete("/api/storagetype/2")
    assert response.status_code == 409


def test_delete_storage_type(client, db_session):
    item = db_session.get(StorageElement, 2)
    db_session.delete(item)

    response = client.delete("/api/storagetype/2")
    print(response.content)
    assert response.status_code == 200

    response = client.get("/api/storagetype/")
    data = response.json()
    assert data["total"] == 1
    assert all(e["id"] != 2 for e in data["items"])


def test_create_storagetype_placeholder(client, db_session):
    placeholder = {"name": "Project Box"}
    response = client.post("/api/storagetype/", json=placeholder)

    print(response.content)
    assert response.status_code == 200
