import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_payment():
    """Testa a criação de um pagamento sem autenticação."""
    payload = {
        "order_id": "61e6a6e3e2b5b9e1f4cdd998",
        "amount": 100.0,
        "currency": "BRL",
        "customer_id": 1,
        "email": "cliente@example.com"
    }

    response = client.post("/tests/", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert "payment_id" in response_data

    return response_data["payment_id"]

def test_get_payment():
    """Testa a busca de um pagamento pelo ID sem autenticação."""
    payment_id = test_create_payment()
    
    response = client.get(f"/tests/?payment_id={payment_id}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["payment_id"] == payment_id
    assert response_data["status"] == "pending"
