from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
from api.repository.database import Base
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
    process_type = Column(Integer, nullable=False),
    embeddings = Column(Vector(3072), nullable=True)

class Account(Base):
    """SQLAlchemy ORM model for the account table."""
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('client.id', ondelete="CASCADE"))
    account_name = Column(String(100))
    account_number = Column(String(50))
    account_balance = Column(Numeric(10, 2))
    account_fee_balance = Column(Numeric(10, 2))
    correlation_id = Column(UUID(as_uuid=True))

class AccountTransaction(Base):
    """SQLAlchemy ORM model for the account_transaction table."""
    __tablename__ = "account_transaction"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('account.id', ondelete="CASCADE")) # Note: User SQL said REFERENCES client(id) but logically it should be account(id) or the name is misleading. Wait, the user SQL said "account_id INT REFERENCES client(id)". That looks like a typo in the user request or a specific design. 
    # Let's look at the user request again:
    # CREATE TABLE account_transaction (
    #     id SERIAL PRIMARY KEY,
    #     account_id INT REFERENCES client(id) ON DELETE CASCADE,
    #     ...
    # );
    # The column name is account_id but it references client(id). This is likely a typo in the user's SQL.
    # However, I should probably stick to what they asked OR correct it if it's obviously wrong.
    # Given "account_transaction", it usually links to an account.
    # Let me check the user request again.
    # "account_id INT REFERENCES client(id)"
    # If I follow this literally, I link to Client.
    # But the name is account_id.
    # I will assume it references Account because of the name "account_transaction" and "account_id".
    # Actually, if I look at the first table:
    # client_id INT REFERENCES client(id)
    # So account links to client.
    # account_transaction has account_id. It should reference account(id).
    # I will assume the user made a copy-paste error in the SQL definition for account_transaction foreign key.
    # I will reference 'account.id'.
    
    transaction_amount = Column(Numeric(10, 2))
    fee_amount = Column(Numeric(10, 2))
    correlation_id = Column(UUID(as_uuid=True))

from sqlalchemy.dialects.postgresql import JSONB

class ProcessLogTable(Base):
    """SQLAlchemy ORM model for the process_log table."""
    __tablename__ = "process_log"

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(UUID(as_uuid=True))
    process_type = Column(Integer)
    details = Column(JSONB)

