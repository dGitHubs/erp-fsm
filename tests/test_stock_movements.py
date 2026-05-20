from uuid import uuid4

from fastapi.testclient import TestClient


def setup_order(client: TestClient, quantity_on_hand: float, bom_quantity: float) -> tuple[int, int, int]:
    """Returns (order_id, material_id, product_id)."""
    customer = client.post(
        "/customers/",
        json={
            "name": "Client stock",
            "email": f"stock-{uuid4().hex[:8]}@example.com",
            "phone": "514-000-0000",
            "address": "1 rue du stock",
        },
    )
    assert customer.status_code == 201

    product = client.post(
        "/products/",
        json={
            "sku": f"PROD-{uuid4().hex[:8]}",
            "name": "Produit stock",
            "description": "",
            "unit": "unit",
            "width": 1.0,
            "height": 1.0,
            "depth": 1.0,
        },
    )
    assert product.status_code == 201
    product_id = product.json()["id"]

    material = client.post(
        "/materials/",
        json={
            "sku": f"MAT-{uuid4().hex[:8]}",
            "name": "Matière stock",
            "description": "",
            "unit": "unit",
            "unit_cost": 1.0,
            "quantity_on_hand": quantity_on_hand,
        },
    )
    assert material.status_code == 201
    material_id = material.json()["id"]

    client.post(
        "/product-materials/",
        json={"product_id": product_id, "material_id": material_id, "quantity": bom_quantity},
    )

    order = client.post(
        "/manufacturing-orders/",
        json={
            "reference": f"MO-{uuid4().hex[:8]}",
            "customer_id": customer.json()["id"],
            "product_id": product_id,
            "quantity": 2,
            "status": "draft",
        },
    )
    assert order.status_code == 201

    return order.json()["id"], material_id, product_id


def test_consume_creates_stock_movement(client: TestClient) -> None:
    order_id, material_id, _ = setup_order(client, quantity_on_hand=100.0, bom_quantity=5.0)

    client.post(f"/manufacturing-orders/{order_id}/consume")

    response = client.get(f"/materials/{material_id}/stock-movements")
    assert response.status_code == 200
    movements = response.json()
    assert len(movements) == 1
    assert movements[0]["material_id"] == material_id
    assert movements[0]["quantity"] == -10.0        # -(5.0 × 2)
    assert movements[0]["movement_type"] == "consumption"


def test_stock_movement_reference_matches_order(client: TestClient) -> None:
    order_id, material_id, _ = setup_order(client, quantity_on_hand=50.0, bom_quantity=3.0)

    order = client.get(f"/manufacturing-orders/{order_id}").json()
    client.post(f"/manufacturing-orders/{order_id}/consume")

    movements = client.get(f"/materials/{material_id}/stock-movements").json()
    assert movements[0]["reference"] == order["reference"]


def test_multiple_consumptions_create_multiple_movements(client: TestClient) -> None:
    order_id_1, material_id, product_id = setup_order(
        client, quantity_on_hand=200.0, bom_quantity=2.0
    )

    customer = client.post(
        "/customers/",
        json={
            "name": "Client 2",
            "email": f"c2-{uuid4().hex[:8]}@example.com",
            "phone": "000",
            "address": "2 rue",
        },
    ).json()
    order_2 = client.post(
        "/manufacturing-orders/",
        json={
            "reference": f"MO-{uuid4().hex[:8]}",
            "customer_id": customer["id"],
            "product_id": product_id,
            "quantity": 2,
            "status": "draft",
        },
    ).json()

    client.post(f"/manufacturing-orders/{order_id_1}/consume")
    client.post(f"/manufacturing-orders/{order_2['id']}/consume")

    movements = client.get(f"/materials/{material_id}/stock-movements").json()
    assert len(movements) == 2
    assert movements[0]["quantity"] == -4.0
    assert movements[1]["quantity"] == -4.0


def test_no_movement_created_on_insufficient_stock(client: TestClient) -> None:
    order_id, material_id, _ = setup_order(client, quantity_on_hand=1.0, bom_quantity=5.0)

    client.post(f"/manufacturing-orders/{order_id}/consume")  # doit échouer (409)

    movements = client.get(f"/materials/{material_id}/stock-movements").json()
    assert len(movements) == 0


def test_stock_movements_empty_when_none(client: TestClient) -> None:
    material = client.post(
        "/materials/",
        json={
            "sku": f"MAT-{uuid4().hex[:8]}",
            "name": "Matière sans mouvement",
            "description": "",
            "unit": "unit",
            "unit_cost": 1.0,
            "quantity_on_hand": 10.0,
        },
    )
    material_id = material.json()["id"]

    response = client.get(f"/materials/{material_id}/stock-movements")
    assert response.status_code == 200
    assert response.json() == []


def test_stock_movements_material_not_found(client: TestClient) -> None:
    response = client.get("/materials/999/stock-movements")
    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}


# --- Réception de stock ---


def create_material(client: TestClient, quantity_on_hand: float = 0.0) -> int:
    response = client.post(
        "/materials/",
        json={
            "sku": f"MAT-{uuid4().hex[:8]}",
            "name": "Matière réception",
            "description": "",
            "unit": "unit",
            "unit_cost": 1.0,
            "quantity_on_hand": quantity_on_hand,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_receive_creates_receipt_movement(client: TestClient) -> None:
    material_id = create_material(client)

    response = client.post(
        f"/materials/{material_id}/receive",
        json={"quantity": 50.0, "reference": "BL-2024-001"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["material_id"] == material_id
    assert data["quantity"] == 50.0
    assert data["movement_type"] == "receipt"
    assert data["reference"] == "BL-2024-001"


def test_receive_increments_quantity_on_hand(client: TestClient) -> None:
    material_id = create_material(client, quantity_on_hand=10.0)

    client.post(f"/materials/{material_id}/receive", json={"quantity": 25.0})

    material = client.get(f"/materials/{material_id}").json()
    assert material["quantity_on_hand"] == 35.0


def test_receive_appears_in_stock_movements(client: TestClient) -> None:
    material_id = create_material(client)

    client.post(f"/materials/{material_id}/receive", json={"quantity": 100.0})
    client.post(f"/materials/{material_id}/receive", json={"quantity": 50.0})

    movements = client.get(f"/materials/{material_id}/stock-movements").json()
    assert len(movements) == 2
    assert all(m["movement_type"] == "receipt" for m in movements)


def test_receive_rejects_zero_quantity(client: TestClient) -> None:
    material_id = create_material(client)

    response = client.post(f"/materials/{material_id}/receive", json={"quantity": 0.0})

    assert response.status_code == 422


def test_receive_material_not_found(client: TestClient) -> None:
    response = client.post("/materials/999/receive", json={"quantity": 10.0})

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}