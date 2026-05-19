from uuid import uuid4

from fastapi.testclient import TestClient


def create_customer(client: TestClient) -> int:
    response = client.post(
        "/customers/",
        json={
            "name": "Client Atelier",
            "email": "atelier@example.com",
            "phone": "555-0202",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_product(client: TestClient) -> int:
    response = client.post(
        "/products/",
        json={
            "sku": f"SKU-{uuid4().hex[:8]}",
            "name": "Table sur mesure",
            "description": "Produit de test",
            "unit": "unit",
            "width": 120.0,
            "height": 80.0,
            "depth": 2.0,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_manufacturing_order(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client)

    response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0001",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 10,
            "description": "Fabrication d'un meuble sur mesure",
            "status": "draft",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["reference"] == "MO-2026-0001"
    assert data["customer_id"] == customer_id
    assert data["product_id"] == product_id
    assert data["quantity"] == 10
    assert data["status"] == "draft"


def test_create_manufacturing_order_customer_not_found(client: TestClient) -> None:
    product_id = create_product(client)

    response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0002",
            "customer_id": 999,
            "product_id": product_id,
            "quantity": 5,
            "description": "Commande invalide",
            "status": "draft",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}


def test_create_manufacturing_order_product_not_found(client: TestClient) -> None:
    customer_id = create_customer(client)

    response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0008",
            "customer_id": customer_id,
            "product_id": 999,
            "quantity": 5,
            "description": "Produit introuvable",
            "status": "draft",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_create_manufacturing_order_duplicate_reference(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client)

    first_response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0003",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 3,
            "description": "Première commande",
            "status": "draft",
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0003",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 7,
            "description": "Commande dupliquée",
            "status": "draft",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Manufacturing order reference already exists",
    }


def test_list_manufacturing_orders(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client)

    client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0004",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 2,
            "description": "Commande A",
            "status": "draft",
        },
    )
    client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0005",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 4,
            "description": "Commande B",
            "status": "confirmed",
        },
    )

    response = client.get("/manufacturing-orders/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["reference"] == "MO-2026-0004"
    assert data[0]["product_id"] == product_id
    assert data[0]["quantity"] == 2
    assert data[1]["reference"] == "MO-2026-0005"
    assert data[1]["product_id"] == product_id
    assert data[1]["quantity"] == 4


def test_get_manufacturing_order_by_id(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client)

    create_response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0006",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 8,
            "description": "Commande lookup",
            "status": "in_progress",
        },
    )
    order_id = create_response.json()["id"]

    response = client.get(f"/manufacturing-orders/{order_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["reference"] == "MO-2026-0006"
    assert data["product_id"] == product_id
    assert data["quantity"] == 8


def test_get_manufacturing_order_by_id_not_found(client: TestClient) -> None:
    response = client.get("/manufacturing-orders/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Manufacturing order not found"}


def test_create_manufacturing_order_rejects_invalid_status(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client)

    response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0007",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 1,
            "description": "Statut invalide",
            "status": "unknown_status",
        },
    )

    assert response.status_code == 422


def test_create_manufacturing_order_rejects_non_positive_quantity(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client)

    response = client.post(
        "/manufacturing-orders/",
        json={
            "reference": "MO-2026-0009",
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": 0,
            "description": "Quantité invalide",
            "status": "draft",
        },
    )

    assert response.status_code == 422