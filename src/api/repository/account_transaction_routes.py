from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from api.repository.models import AccountTransaction as AccountTransactionModel
from api.repository.db_models import AccountTransaction as AccountTransactionTable
from api.repository.database import get_db
from api.repository.account_transaction import AccountTransactionRepository

# Create a router for account transaction endpoints
router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", response_model=AccountTransactionModel)
def create_transaction(transaction: AccountTransactionModel, db: Session = Depends(get_db)):
    """Create a new transaction."""
    repo = AccountTransactionRepository(db)
    # Convert Pydantic model to SQLAlchemy model
    db_transaction = AccountTransactionTable(**transaction.dict(exclude={"id"}))
    return repo.create(db_transaction)

@router.post("/bulk", response_model=List[AccountTransactionModel])
def bulk_create_transactions(transactions: List[AccountTransactionModel], db: Session = Depends(get_db)):
    """Bulk create transactions."""
    repo = AccountTransactionRepository(db)
    # Convert Pydantic models to SQLAlchemy models
    db_transactions = [AccountTransactionTable(**transaction.dict(exclude={"id"})) for transaction in transactions]
    return repo.bulk_create(db_transactions)

@router.get("/{transaction_id}", response_model=AccountTransactionModel)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a transaction by ID."""
    repo = AccountTransactionRepository(db)
    transaction = repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail=f"Transaction with id {transaction_id} not found")
    return transaction

@router.get("/account/{account_id}", response_model=List[AccountTransactionModel])
def get_transactions_by_account(account_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get transactions for a specific account."""
    repo = AccountTransactionRepository(db)
    return repo.get_by_account_id(account_id, skip, limit)
