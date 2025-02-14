from fastapi import APIRouter, HTTPException, Security, Query
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from typing import List, Optional, Union

from ..models import schemas, models
from ..services import repository, security
from ..tools.logging import logger

router = APIRouter()

# Mensagens de erro
PAYMENT_NOT_FOUND_MSG = "Pagamento não encontrado"
ORDER_NOT_FOUND_MSG = "Nenhum pagamento encontrado para este pedido"
INTERNAL_SERVER_ERROR_MSG = "Erro Interno do Servidor"

@router.post("/", response_model=schemas.PaymentResponse)
def create_payment(
    payment_request: schemas.PaymentRequest,
):
    """Cria um pagamento e gera QR Code e link via MercadoPago."""
    logger.info(f"Usuário criando pagamento para pedido {payment_request.order_id}")

    payment_data = models.PaymentModel(
        order_id=payment_request.order_id,
        amount=payment_request.amount,
        customer_id=payment_request.customer_id,
        currency=payment_request.currency,
        email=payment_request.email,
        description=payment_request.description
    )

    payment = repository.create_payment(payment_data)

    if not payment:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=INTERNAL_SERVER_ERROR_MSG)

    return payment

@router.patch("/{payment_id}", response_model=models.PaymentModel)
def update_payment(
    payment_id: str, 
    new_status: models.PaymentStatus,
    current_user: dict = Security(security.verify_token)
    ):
    """
    Atualiza manualmente o status de um pagamento.
    """
    try:
        logger.info(f"Usuário {current_user['id']} atualizando pagamento {payment_id} para status {new_status.value}")

        # Buscar o pagamento no banco
        payment = repository.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Pagamento não encontrado")

        # Atualizar status no MongoDB
        updated = repository.update_payment_status(payment_id, new_status)
        if not updated:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Falha ao atualizar pagamento")

        # Buscar pagamento atualizado e retornar
        updated_payment = repository.get_payment(payment_id)
        return updated_payment

    except Exception as e:
        logger.error(f"Erro ao atualizar pagamento manualmente: {e}", exc_info=True)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar pagamento")

@router.get("/", response_model=Union[schemas.PaymentResponse, List[schemas.PaymentResponse]])
def get_payment(
    payment_id: Optional[str] = Query(None, description="ID do pagamento"),
    order_id: Optional[str] = Query(None, description="ID do pedido"),
    customer_id: Optional[int] = Query(None, description="ID do cliente"),
    current_user: dict = Security(security.verify_token)
):
    """Busca um pagamento pelo ID ou todos os pagamentos associados a um pedido."""
    if payment_id:
        logger.info(f"Usuário {current_user['id']} buscando pagamento {payment_id}")

        payment = repository.get_payment(payment_id)

        if not payment:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=PAYMENT_NOT_FOUND_MSG)

        payment["payment_id"] = str(payment.pop("_id", None))

        return payment

    elif order_id:
        logger.info(f"Usuário {current_user['id']} buscando pagamentos para pedido {order_id}")

        payments = repository.get_payments_by_order(order_id)

        if not payments:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=ORDER_NOT_FOUND_MSG)

        for p in payments:
            p["payment_id"] = str(p.pop("_id", None))
            p["qr_code"] = p.get("qr_code", "")

        return payments

    elif customer_id:
        logger.info(f"Usuário {current_user['id']} buscando pagamentos para cliente {customer_id}")

        payments = repository.get_payments_by_customer(customer_id)

        if not payments:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=ORDER_NOT_FOUND_MSG)

        for p in payments:
            p["payment_id"] = str(p.pop("_id", None))
            p["qr_code"] = p.get("qr_code", "")

        return payments

    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="É necessário informar payment_id ou order_id")

@router.post("/webhook")
def mercadopago_webhook(data: dict):
    """Recebe notificações do MercadoPago e atualiza o status do pagamento no MongoDB."""
    try:
        payment_id = data.get("data", {}).get("id")

        if not payment_id:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Payload inválido")

        # Buscar status atualizado no MercadoPago
        logger.info(f"Recebendo notificação do MercadoPago para pagamento {payment_id}")

        from ..services.repository import get_payment
        payment_info = get_payment(payment_id)

        if not payment_info:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao obter status do MercadoPago")

        # Pegando apenas a string do status
        new_status = payment_info.get("status", "").lower()

        if not new_status:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Status não encontrado no payload do MercadoPago")

        # Atualizar status no MongoDB
        updated = repository.update_payment_status(payment_id, models.PaymentStatus(new_status))

        if not updated:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Erro ao atualizar pagamento no banco de dados")

        return {"message": "Pagamento atualizado com sucesso", "payment_id": payment_id, "status": new_status}

    except Exception as e:
        logger.error(f"Erro no webhook do MercadoPago: {e}", exc_info=True)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro Interno do Servidor")
