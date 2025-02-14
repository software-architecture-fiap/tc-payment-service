from fastapi import APIRouter
import uuid

router = APIRouter()

@router.post("/")
def create_test_payment(payment_data: dict):
    """Cria um pagamento fictício para testes"""
    return {"payment_id": str(uuid.uuid4()), "status": "pending"}

@router.get("/")
def get_test_payment(payment_id: str):
    """Retorna um pagamento fictício"""
    return {"payment_id": payment_id, "status": "pending"}
