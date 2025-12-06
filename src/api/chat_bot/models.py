from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from api.repository.database import Base

class TableDetailsTable(Base):
    __tablename__ = "table_details"

    id = Column(Integer, primary_key=True, index=True)
    table_description = Column(Text, nullable=False)
    embedding = Column(Vector(3072), nullable=True)

class TableDetails(BaseModel):
    id: Optional[int] = None
    table_description: str
    embedding: Optional[List[float]] = None

    model_config = ConfigDict(from_attributes=True)
