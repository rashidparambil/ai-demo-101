from sqlalchemy import Column, ForeignKey, Integer, String
from .database import Base
from pgvector.sqlalchemy import Vector



class CompanyTable(Base):
    """SQLAlchemy ORM model for the companies table."""
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    #address = Column(String(500), nullable=True)
    #email = Column(String(255), nullable=True)
    #phone = Column(String(20), nullable=True)

class CompanyRuleTable:
    """SQLAlchemy ORM model for the companies table."""
    __tablename__ = "company_rule"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('company.id'))
    rule_content = Column(String(255), nullable=False)
    embeddings = Column(Vector(3072), nullable=True)

