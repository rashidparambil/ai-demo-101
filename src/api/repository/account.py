from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from api.repository.db_models import Account
from uuid import UUID

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, account: Account) -> Account:
        """Create a new account."""
        try:
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            return account
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get an account by ID."""
        return self.db.query(Account).filter(Account.id == account_id).first()

        

    def update(self, account_id: int, **kwargs) -> Optional[Account]:
        """Update an account."""
        try:
            account = self.get_by_id(account_id)
            if account:
                for key, value in kwargs.items():
                    setattr(account, key, value)
                self.db.commit()
                self.db.refresh(account)
            return account
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete(self, account_id: int) -> bool:
        """Delete an account."""
        try:
            account = self.get_by_id(account_id)
            if account:
                self.db.delete(account)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def list(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """List accounts."""
        return self.db.query(Account).offset(skip).limit(limit).all()

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """Get an account by account number."""
        return self.db.query(Account).filter(Account.account_number == account_number).first()

    def get_by_account_numbers(self, account_numbers: List[str]) -> List[Account]:
        """Get accounts by a list of account numbers."""
        return self.db.query(Account).filter(Account.account_number.in_(account_numbers)).all()

    def bulk_create(self, accounts: List[Account]) -> List[Account]:
        """Bulk create accounts."""
        try:
            self.db.add_all(accounts)
            self.db.commit()
            for account in accounts:
                self.db.refresh(account)
            return accounts
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
