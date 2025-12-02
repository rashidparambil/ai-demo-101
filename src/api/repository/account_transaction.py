from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from api.repository.db_models import AccountTransaction
from uuid import UUID

class AccountTransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transaction: AccountTransaction) -> AccountTransaction:
        """Create a new account transaction."""
        try:
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            return transaction
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, transaction_id: int) -> Optional[AccountTransaction]:
        """Get a transaction by ID."""
        return self.db.query(AccountTransaction).filter(AccountTransaction.id == transaction_id).first()

    def update(self, transaction_id: int, **kwargs) -> Optional[AccountTransaction]:
        """Update a transaction."""
        try:
            transaction = self.get_by_id(transaction_id)
            if transaction:
                for key, value in kwargs.items():
                    setattr(transaction, key, value)
                self.db.commit()
                self.db.refresh(transaction)
            return transaction
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete(self, transaction_id: int) -> bool:
        """Delete a transaction."""
        try:
            transaction = self.get_by_id(transaction_id)
            if transaction:
                self.db.delete(transaction)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def list(self, skip: int = 0, limit: int = 100) -> List[AccountTransaction]:
        """List transactions."""
        return self.db.query(AccountTransaction).offset(skip).limit(limit).all()

    def get_by_account_id(self, account_id: int, skip: int = 0, limit: int = 100) -> List[AccountTransaction]:
        """List transactions for a specific account."""
        return self.db.query(AccountTransaction).filter(AccountTransaction.account_id == account_id).offset(skip).limit(limit).all()

    def bulk_create(self, transactions: List[AccountTransaction]) -> List[AccountTransaction]:
        """Bulk create transactions."""
        try:
            self.db.add_all(transactions)
            self.db.commit()
            for transaction in transactions:
                self.db.refresh(transaction)
            return transactions
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
