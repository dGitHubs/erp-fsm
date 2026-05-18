from fastapi.testclient import TestClient


def test_create_customer(client: TestClient) -> None:
    response = client.post(
        "/customers/",
        json={
            "name": "Client Test",
            "email": "client@example.com",
            "phone": "555-0101",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Client Test"
    assert data["email"] == "client@example.com"
    assert data["phone"] == "555-0101"
    assert "created_at" in data


def test_list_customers(client: TestClient) -> None:
    client.post(
        "/customers/",
        json={
            "name": "Client A",
            "email": "a@example.com",
            "phone": "111-1111",
        },
    )
    client.post(
        "/customers/",
        json={
            "name": "Client B",
            "email": "b@example.com",
            "phone": "222-2222",
        },
    )

    response = client.get("/customers/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Client A"
    assert data[1]["name"] == "Client B"


def test_get_customer_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/customers/",
        json={
            "name": "Client Lookup",
            "email": "lookup@example.com",
            "phone": "333-3333",
        },
    )
    customer_id = create_response.json()["id"]

    response = client.get(f"/customers/{customer_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == "Client Lookup"


def test_get_customer_by_id_not_found(client: TestClient) -> None:
    response = client.get("/customers/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}
