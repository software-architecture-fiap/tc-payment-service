from pydantic import BaseModel, Field
from typing import Optional
from ..models import models

# Schema para solicitar um pagamento ao MercadoPago
class PaymentRequest(BaseModel):
    order_id: str = Field(..., example="61e6a6e3e2b5b9e1f4cdd998")
    amount: float = Field(..., example=25.00)
    description: str = Field(..., example="Pedido #123")
    customer_id: int = Field(..., example=1)
    currency: str = Field(default="BRL", example="BRL")
    email: Optional[str]

# Schema de resposta do MercadoPago
class PaymentResponse(BaseModel):
    payment_id: str  # ID do pagamento gerado pelo MercadoPago
    order_id: str
    amount: float
    status: models.PaymentStatus  # Enum com os status possíveis
    qr_code: Optional[str]  # QR Code (string em Base64 para exibição no frontend)
    payment_link: Optional[str]  # Link de pagamento gerado pelo MercadoPago
