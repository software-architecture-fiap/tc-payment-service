from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

# Definição dos possíveis status de pagamento
class PaymentStatus(str, Enum):
    pending = "pending"       # Aguardando pagamento
    approved = "approved"     # Pago
    rejected = "rejected"     # Recusado
    in_process = "in_process" # Em análise
    refunded = "refunded"     # Reembolsado

# Modelo para representar um pagamento armazenado no MongoDB
class PaymentModel(BaseModel):
    id: Optional[str] = None # ID do MongoDB (será preenchido automaticamente)
    order_id: str = Field(..., example="61e6a6e3e2b5b9e1f4cdd998")
    customer_id: int = Field(..., example=1)
    amount: float = Field(..., example=25.00)
    currency: str = Field(default="BRL", example="BRL")
    status: PaymentStatus = Field(default=PaymentStatus.pending)  # Status inicial do pagamento
    qr_code: Optional[str] = None # QR Code em Base64 para exibição
    email: Optional[str] = None
    payment_link: Optional[str] = None # Link de pagamento gerado pelo MercadoPago
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}  # Converte `datetime` para string ISO

    @classmethod
    def from_mongo(cls, data: dict):
        """Converte um documento do MongoDB para um modelo Pydantic."""
        if "_id" in data:
            data["id"] = str(data.pop("_id"))  # Converte ObjectId para string
        return cls(**data)