from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

load_dotenv()
database_url = os.getenv("database_url")

# Create engine and session factory
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to inject database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
