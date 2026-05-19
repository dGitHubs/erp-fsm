from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_product(client: TestClient) -> None:
    response = client.post(
        "/products/",
        json={
            "sku": "SKU-001",
            "name": "Panneau chêne",
            "description": "Panneau chêne massif",
            "unit": "square_foot",
            "width": 120.5,
            "height": 80.0,
            "depth": 2.2,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-001"
    assert data["name"] == "Panneau chêne"
    assert data["unit"] == "square_foot"
    assert data["width"] == 120.5
    assert data["height"] == 80.0
    assert data["depth"] == 2.2


def test_create_product_duplicate_sku(client: TestClient) -> None:
    first_response = client.post(
        "/products/",
        json={
            "sku": "SKU-002",
            "name": "Produit A",
            "description": "Premier produit",
            "unit": "unit",
            "width": 10.0,
            "height": 20.0,
            "depth": 1.0,
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/products/",
        json={
            "sku": "SKU-002",
            "name": "Produit B",
            "description": "Produit dupliqué",
            "unit": "unit",
            "width": 15.0,
            "height": 25.0,
            "depth": 1.5,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Product SKU already exists"}


def test_list_products(client: TestClient) -> None:
    client.post(
        "/products/",
        json={
            "sku": "SKU-003",
            "name": "Produit 1",
            "description": "Desc 1",
            "unit": "unit",
            "width": 100.0,
            "height": 50.0,
            "depth": 5.0,
        },
    )
    client.post(
        "/products/",
        json={
            "sku": "SKU-004",
            "name": "Produit 2",
            "description": "Desc 2",
            "unit": "inch",
            "width": 40.0,
            "height": 30.0,
            "depth": 2.0,
        },
    )

    response = client.get("/products/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["sku"] == "SKU-003"
    assert data[0]["width"] == 100.0
    assert data[0]["height"] == 50.0
    assert data[0]["depth"] == 5.0
    assert data[1]["sku"] == "SKU-004"
    assert data[1]["width"] == 40.0
    assert data[1]["height"] == 30.0
    assert data[1]["depth"] == 2.0


def test_get_product_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/products/",
        json={
            "sku": "SKU-005",
            "name": "Produit lookup",
            "description": "Desc lookup",
            "unit": "foot",
            "width": 200.0,
            "height": 100.0,
            "depth": 3.0,
        },
    )
    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["sku"] == "SKU-005"
    assert data["width"] == 200.0
    assert data["height"] == 100.0
    assert data["depth"] == 3.0


def test_get_product_by_id_not_found(client: TestClient) -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_product_rejects_invalid_unit(client: TestClient) -> None:
    response = client.post(
        "/products/",
        json={
            "sku": "SKU-006",
            "name": "Produit invalide",
            "description": "Desc invalide",
            "unit": "invalid_unit",
        },
    )

    assert response.status_code == 422


def test_create_product_rejects_non_positive_width(client: TestClient) -> None:
    response = client.post(
        "/products/",
        json={
            "sku": "SKU-007",
            "name": "Produit largeur invalide",
            "description": "Desc",
            "unit": "unit",
            "width": 0,
            "height": 10.0,
            "depth": 1.0,
        },
    )

    assert response.status_code == 422


def test_create_product_rejects_non_positive_height(client: TestClient) -> None:
    response = client.post(
        "/products/",
        json={
            "sku": "SKU-008",
            "name": "Produit hauteur invalide",
            "description": "Desc",
            "unit": "unit",
            "width": 10.0,
            "height": -5.0,
            "depth": 1.0,
        },
    )

    assert response.status_code == 422


def test_create_product_rejects_non_positive_depth(client: TestClient) -> None:
    response = client.post(
        "/products/",
        json={
            "sku": "SKU-009",
            "name": "Produit profondeur invalide",
            "description": "Desc",
            "unit": "unit",
            "width": 10.0,
            "height": 5.0,
            "depth": 0,
        },
    )

    assert response.status_code == 422

def create_material_for_cost(client: TestClient, sku: str, unit_cost: float) -> int:
    response = client.post(
        "/materials/",
        json={
            "sku": sku,
            "name": f"Material {sku}",
            "description": "Material for cost test",
            "unit": "unit",
            "unit_cost": unit_cost,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_get_product_material_cost(client: TestClient) -> None:
    product_response = client.post(
        "/products/",
        json={
            "sku": f"SKU-{uuid4().hex[:8]}",
            "name": "Produit coût",
            "description": "Produit pour calcul coût",
            "unit": "unit",
            "width": 100.0,
            "height": 50.0,
            "depth": 10.0,
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    material_id_1 = create_material_for_cost(client, f"MAT-{uuid4().hex[:8]}", 4.5)
    material_id_2 = create_material_for_cost(client, f"MAT-{uuid4().hex[:8]}", 12.0)

    response_1 = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id_1,
            "quantity": 3.0,
        },
    )
    assert response_1.status_code == 201, response_1.text

    response_2 = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id_2,
            "quantity": 2.0,
        },
    )
    assert response_2.status_code == 201, response_2.text

    response = client.get(f"/products/{product_id}/material-cost")

    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["material_cost"] == 37.5
    assert len(data["lines"]) == 2

    assert data["lines"][0]["material_id"] == material_id_1
    assert data["lines"][0]["quantity"] == 3.0
    assert data["lines"][0]["unit_cost"] == 4.5
    assert data["lines"][0]["line_cost"] == 13.5

    assert data["lines"][1]["material_id"] == material_id_2
    assert data["lines"][1]["quantity"] == 2.0
    assert data["lines"][1]["unit_cost"] == 12.0
    assert data["lines"][1]["line_cost"] == 24.0


def test_get_product_material_cost_with_no_materials(client: TestClient) -> None:
    product_response = client.post(
        "/products/",
        json={
            "sku": f"SKU-{uuid4().hex[:8]}",
            "name": "Produit sans BOM",
            "description": "Produit sans matières",
            "unit": "unit",
            "width": 100.0,
            "height": 50.0,
            "depth": 10.0,
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    response = client.get(f"/products/{product_id}/material-cost")

    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product_id
    assert data["material_cost"] == 0.0
    assert data["lines"] == []


def test_get_product_material_cost_product_not_found(client: TestClient) -> None:
    response = client.get("/products/999/material-cost")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}