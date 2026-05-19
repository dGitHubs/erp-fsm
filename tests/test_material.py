from fastapi.testclient import TestClient


def test_create_material(client: TestClient) -> None:
    response = client.post(
        "/materials/",
        json={
            "sku": "MAT-001",
            "name": "Contreplaqué bouleau",
            "description": "Panneau de contreplaqué",
            "unit": "square_foot",
            "unit_cost": 12.5,
            "quantity_on_hand": 25.0,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "MAT-001"
    assert data["name"] == "Contreplaqué bouleau"
    assert data["unit"] == "square_foot"
    assert data["unit_cost"] == 12.5


def test_create_material_duplicate_sku(client: TestClient) -> None:
    first_response = client.post(
        "/materials/",
        json={
            "sku": "MAT-002",
            "name": "Matériau A",
            "description": "Premier matériau",
            "unit": "unit",
            "unit_cost": 5.0,
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/materials/",
        json={
            "sku": "MAT-002",
            "name": "Matériau B",
            "description": "Matériau dupliqué",
            "unit": "unit",
            "unit_cost": 6.0,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Material SKU already exists"}


def test_list_materials(client: TestClient) -> None:
    client.post(
        "/materials/",
        json={
            "sku": "MAT-003",
            "name": "Matériau 1",
            "description": "Desc 1",
            "unit": "unit",
            "unit_cost": 3.5,
        },
    )
    client.post(
        "/materials/",
        json={
            "sku": "MAT-004",
            "name": "Matériau 2",
            "description": "Desc 2",
            "unit": "foot",
            "unit_cost": 8.25,
        },
    )

    response = client.get("/materials/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["sku"] == "MAT-003"
    assert data[0]["unit_cost"] == 3.5
    assert data[1]["sku"] == "MAT-004"
    assert data[1]["unit_cost"] == 8.25


def test_get_material_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/materials/",
        json={
            "sku": "MAT-005",
            "name": "Matériau lookup",
            "description": "Desc lookup",
            "unit": "inch",
            "unit_cost": 1.75,
        },
    )
    material_id = create_response.json()["id"]

    response = client.get(f"/materials/{material_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == material_id
    assert data["sku"] == "MAT-005"
    assert data["unit_cost"] == 1.75


def test_get_material_by_id_not_found(client: TestClient) -> None:
    response = client.get("/materials/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}


def test_create_material_rejects_invalid_unit(client: TestClient) -> None:
    response = client.post(
        "/materials/",
        json={
            "sku": "MAT-006",
            "name": "Matériau invalide",
            "description": "Desc invalide",
            "unit": "invalid_unit",
            "unit_cost": 2.0,
        },
    )

    assert response.status_code == 422


def test_create_material_rejects_negative_unit_cost(client: TestClient) -> None:
    response = client.post(
        "/materials/",
        json={
            "sku": "MAT-007",
            "name": "Matériau coût invalide",
            "description": "Desc coût invalide",
            "unit": "unit",
            "unit_cost": -1.0,
        },
    )

    assert response.status_code == 422