from sqlalchemy import Column, Integer, String
from .database import Base


class CompanyDB(Base):
    """SQLAlchemy ORM model for the companies table."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
