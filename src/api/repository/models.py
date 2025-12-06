from pgvector.sqlalchemy import Vector
from pydantic import BaseModel

from api.repository.process_type import ProcessType

class Client(BaseModel):
    """Schema for a client including its ID (database response)."""
    id: int
    name: str

class ClientRules(BaseModel):
    """Schema for a client including its ID (database response)."""
    rules: list[str]
    process_type: ProcessType

class MailRequest(BaseModel):
    from_address: str
    subject: str
    content: str    


from uuid import UUID
from typing import Optional
from decimal import Decimal

class Account(BaseModel):
    """Schema for an account."""
    id: Optional[int] = None
    client_id: int
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    account_balance: Optional[Decimal] = None
    account_fee_balance: Optional[Decimal] = None
    correlation_id: Optional[UUID] = None

    class Config:
        from_attributes = True

class AccountTransaction(BaseModel):
    """Schema for an account transaction."""
    id: Optional[int] = None
    account_id: int
    transaction_amount: Optional[Decimal] = None
    fee_amount: Optional[Decimal] = None
    correlation_id: Optional[UUID] = None

    class Config:
        from_attributes = True
