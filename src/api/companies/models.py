from pydantic import BaseModel
from typing import Optional


class CompanyCreate(BaseModel):
    """Schema for creating a company (input only)."""
    name: str
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Company(CompanyCreate):
    """Schema for a company including its ID (database response)."""
    id: int
