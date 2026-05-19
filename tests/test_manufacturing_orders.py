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

    def create_material_for_requirements(
        client: TestClient,
        sku: str,
        unit_cost: float = 1.0,
    ) -> int:
        response = client.post(
            "/materials/",
            json={
                "sku": sku,
                "name": f"Material {sku}",
                "description": "Material for manufacturing requirements test",
                "unit": "unit",
                "unit_cost": unit_cost,
            },
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    def create_product_for_requirements(client: TestClient) -> int:
        response = client.post(
            "/products/",
            json={
                "sku": f"PROD-{uuid4().hex[:8]}",
                "name": "Produit requirements",
                "description": "Produit pour test de besoins matière",
                "unit": "unit",
                "width": 100.0,
                "height": 50.0,
                "depth": 10.0,
            },
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    def add_product_material_for_requirements(
        client: TestClient,
        product_id: int,
        material_id: int,
        quantity: float,
    ) -> None:
        response = client.post(
            "/product-materials/",
            json={
                "product_id": product_id,
                "material_id": material_id,
                "quantity": quantity,
            },
        )
        assert response.status_code == 201, response.text

    def create_customer_for_requirements(client: TestClient) -> int:
        response = client.post(
            "/customers/",
            json={
                "name": "Client requirements",
                "email": f"requirements-{uuid4().hex[:8]}@example.com",
                "phone": "555-123-4567",
                "address": "123 Test Street",
            },
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    def create_manufacturing_order_for_requirements(
        client: TestClient,
        customer_id: int,
        product_id: int,
        quantity: int,
    ) -> int:
        response = client.post(
            "/manufacturing-orders/",
            json={
                "reference": f"MO-{uuid4().hex[:8]}",
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": quantity,
                "description": "Ordre pour test besoins matière",
                "status": "draft",
            },
        )
        assert response.status_code == 201, response.text
        return response.json()["id"]

    def test_get_manufacturing_order_material_requirements(client: TestClient) -> None:
        customer_id = create_customer_for_requirements(client)
        product_id = create_product_for_requirements(client)

        material_id_1 = create_material_for_requirements(client, f"MAT-{uuid4().hex[:8]}")
        material_id_2 = create_material_for_requirements(client, f"MAT-{uuid4().hex[:8]}")

        add_product_material_for_requirements(client, product_id, material_id_1, 2.5)
        add_product_material_for_requirements(client, product_id, material_id_2, 1.0)

        order_id = create_manufacturing_order_for_requirements(
            client,
            customer_id=customer_id,
            product_id=product_id,
            quantity=4,
        )

        response = client.get(f"/manufacturing-orders/{order_id}/material-requirements")

        assert response.status_code == 200
        data = response.json()
        assert data["manufacturing_order_id"] == order_id
        assert data["product_id"] == product_id
        assert data["order_quantity"] == 4
        assert len(data["lines"]) == 2

        assert data["lines"][0]["material_id"] == material_id_1
        assert data["lines"][0]["quantity_per_product"] == 2.5
        assert data["lines"][0]["required_quantity"] == 10.0

        assert data["lines"][1]["material_id"] == material_id_2
        assert data["lines"][1]["quantity_per_product"] == 1.0
        assert data["lines"][1]["required_quantity"] == 4.0

    def test_get_manufacturing_order_material_requirements_with_no_bom(
        client: TestClient,
    ) -> None:
        customer_id = create_customer_for_requirements(client)
        product_id = create_product_for_requirements(client)

        order_id = create_manufacturing_order_for_requirements(
            client,
            customer_id=customer_id,
            product_id=product_id,
            quantity=3,
        )

        response = client.get(f"/manufacturing-orders/{order_id}/material-requirements")

        assert response.status_code == 200
        data = response.json()
        assert data["manufacturing_order_id"] == order_id
        assert data["product_id"] == product_id
        assert data["order_quantity"] == 3
        assert data["lines"] == []

    def test_get_manufacturing_order_material_requirements_not_found(
        client: TestClient,
    ) -> None:
        response = client.get("/manufacturing-orders/999/material-requirements")

        assert response.status_code == 404
        assert response.json() == {"detail": "Manufacturing order not found"}
