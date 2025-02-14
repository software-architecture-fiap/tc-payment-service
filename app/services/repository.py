import os
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timezone
from bson import ObjectId
import mercadopago
from dotenv import load_dotenv
from ..models import models
from ..tools.logging import logger
from ..database.database import payments_collection

load_dotenv()

# Configuração do MercadoPago
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
NGROK_URI = os.getenv('NGROK_URI')
sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

# ------------------------ FUNÇÕES DO REPOSITÓRIO ------------------------

def create_payment(payment_data: models.PaymentModel) -> dict:
    """Cria uma preferência de pagamento e gera um link e QR Code via MercadoPago."""
    try:
        logger.info(f"Conexão com MongoDB estabelecida? {payments_collection is not None}")
        logger.info(f"Criando preferência de pagamento para order_id {payment_data.order_id}")

        # Configurar payload do MercadoPago para criar uma preferência de pagamento
        preference_payload = {
            "items": [
                {
                    "title": f"Pedido {payment_data.order_id}",
                    "quantity": 1,
                    "currency_id": payment_data.currency,
                    "unit_price": payment_data.amount,
                }
            ],
            "payer": {
                "email": payment_data.email
            },
            "payment_methods": {
                "excluded_payment_methods": [],  # Aqui você pode excluir métodos específicos
                "installments": 12  # Máximo de parcelas permitidas
            },
            "back_urls": {
                "success": NGROK_URI,
                "failure": NGROK_URI,
                "pending": NGROK_URI
            },
            "auto_return": "approved",  # Redireciona automaticamente após o pagamento
            "notification_url": NGROK_URI  # Webhook para atualizar status
        }

        # Criar a preferência no MercadoPago
        preference_response = sdk.preference().create(preference_payload)
        preference = preference_response.get("response", {})

        if "id" not in preference:
            logger.error(f"Erro ao criar preferência: {preference_response}")
            return None

        payment_link = preference.get("init_point")

        # 🔹 Gerar o QR Code a partir do link de pagamento
        qr = qrcode.make(payment_link)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Criar documento no MongoDB
        payment_record = {
            "order_id": payment_data.order_id,
            "customer_id": payment_data.customer_id,
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "status": models.PaymentStatus.pending.value,  # Status inicial
            "payment_link": payment_link,  # Link para pagamento no MercadoPago
            "qr_code": qr_code_base64,  # 🔹 QR Code em base64
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Inserir no MongoDB
        inserted = payments_collection.insert_one(payment_record)
        payment_record["_id"] = inserted.inserted_id  # Adicionar ID gerado ao dict

        logger.info(f"Pagamento criado com sucesso! ID: {inserted.inserted_id}")

        # Converter para modelo Pydantic
        payment_model = models.PaymentModel.from_mongo(payment_record).dict()
        payment_model["payment_id"] = payment_model.pop("id", None)

        return payment_model

    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {e}", exc_info=True)
        return None

def get_payment(payment_id: str) -> dict:
    """Recupera um pagamento pelo ID."""
    try:
        logger.info(f"Buscando pagamento {payment_id}")
        payment = payments_collection.find_one({"_id": ObjectId(payment_id)})

        if not payment:
            logger.warning(f"Pagamento {payment_id} não encontrado")
            return None

        payment["id"] = str(payment["_id"])  # Converte ObjectId para string
        return payment
    except Exception as e:
        logger.error(f"Erro ao buscar pagamento: {e}", exc_info=True)
        return None

def update_payment_status(payment_id: str, status: models.PaymentStatus) -> bool:
    """Atualiza o status de um pagamento no MongoDB."""
    try:
        logger.info(f"Atualizando status do pagamento {payment_id} para {status.value}")

        result = payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": {"status": status.value, "updated_at": datetime.now(timezone.utc)}}
        )

        if result.modified_count == 0:
            logger.warning(f"Nenhum pagamento atualizado para ID {payment_id}")
            return False

        logger.info(f"Status do pagamento {payment_id} atualizado para {status.value}")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar status do pagamento: {e}", exc_info=True)
        return False

def get_payments_by_order(order_id: str) -> list:
    """Recupera todos os pagamentos associados a um pedido."""
    try:
        logger.info(f"Buscando pagamentos para order_id {order_id}")
        payments = list(payments_collection.find({"order_id": order_id}))

        for payment in payments:
            payment["_id"] = str(payment["_id"])  # Converte ObjectId para string

        return payments
    except Exception as e:
        logger.error(f"Erro ao buscar pagamentos por pedido: {e}", exc_info=True)
        return []

def get_payments_by_customer(customer_id: str) -> list:
    """Recupera todos os pagamentos associados a um pedido."""
    try:
        logger.info(f"Buscando pagamentos para customer_id {customer_id}")
        payments = list(payments_collection.find({"customer_id": customer_id}))

        for payment in payments:
            payment["_id"] = str(payment["_id"])  # Converte ObjectId para string

        return payments
    except Exception as e:
        logger.error(f"Erro ao buscar pagamentos por pedido: {e}", exc_info=True)
        return []
