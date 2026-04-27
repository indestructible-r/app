from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class WebhookRequest(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str

class WebhookResponse(BaseModel):
    success: bool
    message: str
    account_id: Optional[int] = None
    new_balance: Optional[Decimal] = None