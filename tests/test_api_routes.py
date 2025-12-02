import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from api.main import app
from api.repository.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest

# Setup in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_account():
    response = client.post(
        "/accounts",
        json={"id": 1, "client_id": 1, "account_name": "Test Account", "account_number": "12345", "account_balance": 100.0, "account_fee_balance": 0.0}
    )
    # Note: We might need to create a client first if foreign key constraints are enforced in SQLite
    # SQLite enforces FKs only if enabled. SQLAlchemy might handle it.
    # Let's see if it fails. If so, we'll create a client.
    
    # Actually, let's create a client first to be safe
    client.post("/client", json={"id": 1, "name": "Test Client"})

    response = client.post(
        "/accounts",
        json={"id": 1, "client_id": 1, "account_name": "Test Account", "account_number": "12345", "account_balance": 100.0, "account_fee_balance": 0.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["account_number"] == "12345"
    assert "id" in data

def test_get_account():
    # Create account first (relying on previous test state or creating new)
    # Since we use in-memory DB per session, but here it's shared for the process?
    # StaticPool means it's shared.
    
    response = client.get("/accounts/number/12345")
    assert response.status_code == 200
    data = response.json()
    assert data["account_number"] == "12345"

def test_create_transaction():
    # Account 1 should exist from previous test
    response = client.post(
        "/transactions",
        json={"id": 1, "account_id": 1, "transaction_amount": 50.0, "fee_amount": 1.0}
    )
    assert response.status_code == 200
    data = response.json()
    # Transaction amount is returned as string (Decimal)
    assert float(data["transaction_amount"]) == 50.0

def test_get_transactions_by_account():
    response = client.get("/transactions/account/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["account_id"] == 1

def test_bulk_create_accounts():
    accounts = [
        {"id": 2, "client_id": 1, "account_name": "Bulk Account 1", "account_number": "99901", "account_balance": 100.0, "account_fee_balance": 0.0},
        {"id": 3, "client_id": 1, "account_name": "Bulk Account 2", "account_number": "99902", "account_balance": 200.0, "account_fee_balance": 0.0}
    ]
    response = client.post("/accounts/bulk", json=accounts)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["account_number"] == "99901"
    assert data[1]["account_number"] == "99902"

def test_bulk_create_transactions():
    transactions = [
        {"id": 2, "account_id": 1, "transaction_amount": 10.0, "fee_amount": 1.0},
        {"id": 3, "account_id": 1, "transaction_amount": 20.0, "fee_amount": 2.0}
    ]
    response = client.post("/transactions/bulk", json=transactions)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert float(data[0]["transaction_amount"]) == 10.0
    assert float(data[1]["transaction_amount"]) == 20.0

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_create_account()
        test_get_account()
        test_create_transaction()
        test_get_transactions_by_account()
        test_bulk_create_accounts()
        test_bulk_create_transactions()
        print("All tests passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Test failed: {e}")
        exit(1)
