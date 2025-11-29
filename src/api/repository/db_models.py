from sqlalchemy import Column, ForeignKey, Integer, String
from .database import Base
from pgvector.sqlalchemy import Vector

class ClientTable(Base):
    """SQLAlchemy ORM model for the client table."""
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    #address = Column(String(500), nullable=True)
    #email = Column(String(255), nullable=True)
    #phone = Column(String(20), nullable=True)

class ClientRuleTable:
    """SQLAlchemy ORM model for the client_rule table."""
    __tablename__ = "client_rule"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    rule_content = Column(String(255), nullable=False)
    embeddings = Column(Vector(3072), nullable=True)
