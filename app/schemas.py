from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

    class Config:
        from_attributes = True

class AccountResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class AdminResponse(BaseModel):
    id: int
    email: str
    full_name: str

    class Config:
        from_attributes = True