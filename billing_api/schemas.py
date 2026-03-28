from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BillingCreate(BaseModel):
    user_id: int
    subscription_type: str
    price: float
    card_number: str

class BillingUpdate(BaseModel):
    subscription_type: Optional[str] = None
    price: Optional[float] = None
    card_number: Optional[str] = None
    status: Optional[str] = None

class BillingResponse(BaseModel):
    id: str  # MongoDB returns string ObjectId
    user_id: int
    subscription_type: str
    price: float
    card_number: str
    status: str
    created_at: datetime
