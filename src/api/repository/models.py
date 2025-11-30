from pgvector.sqlalchemy import Vector
from pydantic import BaseModel

from repository.process_type import ProcessType

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