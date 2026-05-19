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