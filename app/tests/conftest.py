import pytest
import mongomock
from fastapi.testclient import TestClient
from app.main import app
from app.database import database
from app.services import security

@pytest.fixture(scope="function", autouse=True)
def mock_mongo(monkeypatch):
    """Mocka a conexão com o MongoDB para testes."""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["test_db"]
    mock_collection = mock_db["payments"]

    monkeypatch.setattr(database, "payments_collection", mock_collection)
    yield mock_collection

@pytest.fixture(scope="function")
def client():
    """Cria um cliente de teste do FastAPI."""
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def mock_auth(monkeypatch):
    """Mocka a autenticação para permitir acesso sem um token."""
    
    def fake_verify_token(*args, **kwargs):
        return {"id": 1, "role": "admin"}  # Simula um usuário autenticado

    # Substitui a função original para sempre autenticar o usuário
    monkeypatch.setattr(security, "verify_token", fake_verify_token)
