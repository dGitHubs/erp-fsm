from uuid import uuid4

from fastapi.testclient import TestClient


def create_product(client: TestClient) -> int:
    response = client.post(
        "/products/",
        json={
            "sku": f"PROD-{uuid4().hex[:8]}",
            "name": "Produit test",
            "description": "Produit pour BOM",
            "unit": "unit",
            "width": 100.0,
            "height": 50.0,
            "depth": 10.0,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_material(client: TestClient) -> int:
    response = client.post(
        "/materials/",
        json={
            "sku": f"MAT-{uuid4().hex[:8]}",
            "name": "Matériau test",
            "description": "Matériau pour BOM",
            "unit": "square_foot",
            "unit_cost": 4.5,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_product_material(client: TestClient) -> None:
    product_id = create_product(client)
    material_id = create_material(client)

    response = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id,
            "quantity": 2.5,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == product_id
    assert data["material_id"] == material_id
    assert data["quantity"] == 2.5


def test_create_product_material_product_not_found(client: TestClient) -> None:
    material_id = create_material(client)

    response = client.post(
        "/product-materials/",
        json={
            "product_id": 999,
            "material_id": material_id,
            "quantity": 1.0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_product_material_material_not_found(client: TestClient) -> None:
    product_id = create_product(client)

    response = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": 999,
            "quantity": 1.0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}


def test_create_product_material_duplicate_pair(client: TestClient) -> None:
    product_id = create_product(client)
    material_id = create_material(client)

    first_response = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id,
            "quantity": 3.0,
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id,
            "quantity": 4.0,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Product material already exists"}


def test_list_product_materials(client: TestClient) -> None:
    product_id_1 = create_product(client)
    material_id_1 = create_material(client)

    product_id_2 = create_product(client)
    material_id_2 = create_material(client)

    client.post(
        "/product-materials/",
        json={
            "product_id": product_id_1,
            "material_id": material_id_1,
            "quantity": 1.5,
        },
    )
    client.post(
        "/product-materials/",
        json={
            "product_id": product_id_2,
            "material_id": material_id_2,
            "quantity": 2.0,
        },
    )

    response = client.get("/product-materials/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["product_id"] == product_id_1
    assert data[0]["material_id"] == material_id_1
    assert data[0]["quantity"] == 1.5
    assert data[1]["product_id"] == product_id_2
    assert data[1]["material_id"] == material_id_2
    assert data[1]["quantity"] == 2.0


def test_get_product_material_by_id(client: TestClient) -> None:
    product_id = create_product(client)
    material_id = create_material(client)

    create_response = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id,
            "quantity": 6.0,
        },
    )
    product_material_id = create_response.json()["id"]

    response = client.get(f"/product-materials/{product_material_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_material_id
    assert data["product_id"] == product_id
    assert data["material_id"] == material_id
    assert data["quantity"] == 6.0


def test_get_product_material_by_id_not_found(client: TestClient) -> None:
    response = client.get("/product-materials/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product material not found"}


def test_create_product_material_rejects_non_positive_quantity(
    client: TestClient,
) -> None:
    product_id = create_product(client)
    material_id = create_material(client)

    response = client.post(
        "/product-materials/",
        json={
            "product_id": product_id,
            "material_id": material_id,
            "quantity": 0,
        },
    )

    assert response.status_code == 422