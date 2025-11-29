from pgvector.sqlalchemy import Vector
from pydantic import BaseModel

class Client(BaseModel):
    """Schema for a client including its ID (database response)."""
    id: int
    name: str


class ClientRule:
    """Schema for a client including its ID (database response)."""
    id: int
    client_id: int
    rule_content: str
    embedding: Vector(3072)

class ClientRules(BaseModel):
    """Schema for a client including its ID (database response)."""
    rules: list[str]