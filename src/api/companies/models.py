from pgvector.sqlalchemy import Vector
from pydantic import BaseModel

class Company(BaseModel):
    """Schema for a company including its ID (database response)."""
    id: int
    name: str


class CompanyRule:
    """Schema for a company including its ID (database response)."""
    id: int
    company_id: int
    rule_content: str
    embedding: Vector(3072)