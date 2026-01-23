import sys
from pathlib import Path

# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# client_mcp_server.py
# MCP server exposing find_client(name: str) -> {id, name, match_score}
from api.config import config
import logging
# from dotenv import load_dotenv
import uvicorn
from api.repository.client_rule_embedding import ClientRuleEmbedding
from api.repository.database import SessionLocal
from api.repository.account import AccountRepository
from api.repository.account_transaction import AccountTransactionRepository
from api.repository.db_models import Account as AccountTable, AccountTransaction as AccountTransactionTable
from api.repository.process_type import ProcessType
from api.repository.process_log_repository import ProcessLogRepository
from api.repository.models import Account as AccountModel, AccountTransaction as AccountTransactionModel, ProcessLog
from api.repository.final_response import FinalResponse, FieldValidation
from api.chat_bot.service import ChatBotService

from typing import List
import json

# mcp provides a simple way to expose tools
from mcp.server.fastmcp import FastMCP

import psycopg2
from psycopg2.extras import RealDictCursor

service = ChatBotService()

# load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client_mcp_server")

# DB_HOST = os.getenv("db_host", "localhost")
# DB_PORT = int(os.getenv("db_port", 5432))
# DB_NAME = os.getenv("db_name")
# DB_USER = os.getenv("db_user")
# DB_PASSWORD = os.getenv("db_password")

# Optional simple API key auth for incoming MCP calls (Streamable HTTP supports headers)
# MCP_SERVER_API_KEY = os.getenv("MCP_SERVER_API_KEY","")  # set on server and client

def get_db_conn():
    return psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        database=config.db_name,
        user=config.db_user,
        password=config.db_password,
        cursor_factory=RealDictCursor
    )

mcp = FastMCP()
app = mcp.streamable_http_app()

@mcp.tool("find_client", description="Find client by name. Args: {name: str}")
def find_client(name: str) -> dict:
    """
    Find a client by name.
    Returns: {"id": int, "name": str, "score": float} or raise if not found.
    """
    print(f"**************************************Finding client with name: {name}*************") 
    # Basic normalization + simple LIKE search; replace with your fuzzy logic if desired
    q = name.strip()
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name FROM client WHERE LOWER(name) LIKE LOWER(%s) ORDER BY id LIMIT 1;",
            (f"%{q}%",),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return {"found": False, "message": f"No client matching '{name}'"}
        # Return top match and list of candidates (optional)
        top = rows[0]
        candidates = [{"id": r["id"], "name": r["name"]} for r in rows]
        return {"found": True, "client_id": int(top["id"]), "client_name": top["name"], "candidates": candidates}

    except Exception as e:
        logger.exception("DB lookup failed")
        raise e  # MCP will return tool error to caller
    
@mcp.tool("find_all_client_rule_by_client_id_and_process_type", description="Find client rules by client Id. Args: {client_id: int, process_type: int}")
def find_all_client_rule_by_client_id(client_id: int, process_type: int) -> dict:
    """
    Find a client rule by client_id.
    Returns: [{"id": int, "rule_content": str, "score": float}] or empty dict if not found.
    """
    print(f"**************************************Finding client rule by client Id: {client_id}, process_type: {process_type}*************") 
    # Basic normalization + simple LIKE search; replace with your fuzzy logic if desired
    try:
        clientRuleEmbedding = ClientRuleEmbedding(client_id)
        data = clientRuleEmbedding.search_rules(process_type,return_all=True, k=100,include_embeddings=False)
        # # 2. Filter the 'results' list
        # filtered_results = [
        #     item for item in data['results'] 
        #     if item['process_type'] == 'Placement'
        # ]

        # # 3. (Optional) Create a new dictionary with the filtered results
        # filtered_data = {
        #     "success": True,
        #     "client_id": data['client_id'],
        #     "include_embeddings": data['include_embeddings'],
        #     "results_count": len(filtered_results), # Update the count
        #     "results": filtered_results
        # }
        return data

    except Exception as e:
        logger.exception("DB client rule lookup failed")
        raise e  # MCP will return tool error to caller

@mcp.tool("get_all_accounts", description="Get all accounts. Args: {skip: int, limit: int}")
def get_all_accounts(skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Get all accounts.
    Returns: List of accounts.
    """
    print(f"**************************************Getting all accounts*************")
    try:
        db = SessionLocal()
        repo = AccountRepository(db)
        accounts = repo.list(skip, limit)
        # Convert to dict for JSON serialization
        return [AccountModel.from_orm(a).dict() for a in accounts]
    except Exception as e:
        logger.exception("Failed to get accounts")
        raise e
    finally:
        db.close()


@mcp.tool("accounts_urc_check", description="Check Unrecognised accounts. Args: {final_response: FinalResponse}")
def accounts_urc_check(final_response: FinalResponse) -> FinalResponse:
    """
    Check Unrecognised accounts.
    Returns: FinalResponse.
    """
    try:
        db = SessionLocal()
        print("Get accounts from database")
        repo = AccountRepository(db)
        
        account_numbers =  [
            field.customer_account
            for field in final_response.extracted_fields # Use .get with a default [] for safety
        ]
        accounts = repo.get_by_account_numbers(account_numbers)
        existing_accounts_set = {
            account.account_number 
            for account in accounts
        }
        all_accounts_set = set(account_numbers)

        if final_response.process_type == ProcessType.Transaction.value:
            missing_accounts_set = all_accounts_set - existing_accounts_set
            missing_accounts_list = list(missing_accounts_set)
            print("Update validation message for missing accounts")
            for record in final_response.extracted_fields:
                if record.customer_account in missing_accounts_list:
                    validation = FieldValidation(message="Account does not exists")
                    record.field_validations.append(validation)
                    print("Account does not exists")
        elif final_response.process_type == ProcessType.Placement.value:
            duplicate_accounts_set = existing_accounts_set - all_accounts_set
            duplicate_accounts_list = list(duplicate_accounts_set)
            print("Update validation message for duplicate accounts")
            for record in final_response.extracted_fields:
                if record.customer_account in duplicate_accounts_list:
                    validation = FieldValidation(message="Account already exists")
                    record.field_validations.append(validation)
                    print("Account already exists")
        return final_response
    except Exception as e:
        logger.exception("Failed to get accounts")
        raise e
    finally:
        db.close()

@mcp.tool("save_accounts_and_transactions", description="Save accounts and transactions. Args: {final_response: FinalResponse, correlation_id: str}")
def save_accounts_and_transactions(final_response: FinalResponse, correlation_id: str) -> FinalResponse:
    """
    Save accounts and transaction to database
    Returns: FinalResponse.
    """
    try:
        db = SessionLocal()
        repo = AccountRepository(db)
        repo.process_accounts(final_response.model_dump_json(), correlation_id)
        print("Account and transaction updated to database")
        return final_response
    except Exception as e:
        logger.exception("Failed to get accounts")
        raise e
    finally:
        db.close()

@mcp.tool("bulk_create_accounts", description="Bulk create accounts. Args: {accounts: List[dict]}")
def bulk_create_accounts(accounts: List[dict]) -> List[dict]:
    """
    Bulk create accounts.
    Returns: List of created accounts.
    """
    print(f"**************************************Bulk creating accounts*************")
    try:
        db = SessionLocal()
        repo = AccountRepository(db)
        # Convert dicts to SQLAlchemy models
        # Note: Pydantic validation happens here implicitly if we use AccountModel first
        account_models = [AccountModel(**a) for a in accounts]
        db_accounts = [AccountTable(**a.dict(exclude={"id"})) for a in account_models]
        
        created_accounts = repo.bulk_create(db_accounts)
        return [AccountModel.from_orm(a).dict() for a in created_accounts]
    except Exception as e:
        logger.exception("Failed to bulk create accounts")
        raise e
    finally:
        db.close()

@mcp.tool("get_all_transactions", description="Get all transactions. Args: {skip: int, limit: int}")
def get_all_transactions(skip: int = 0, limit: int = 100) -> List[dict]:
    """
    Get all transactions.
    Returns: List of transactions.
    """
    print(f"**************************************Getting all transactions*************")
    try:
        db = SessionLocal()
        repo = AccountTransactionRepository(db)
        transactions = repo.list(skip, limit)
        return [AccountTransactionModel.from_orm(t).dict() for t in transactions]
    except Exception as e:
        logger.exception("Failed to get transactions")
        raise e
    finally:
        db.close()

@mcp.tool("bulk_create_transactions", description="Bulk create transactions. Args: {transactions: List[dict]}")
def bulk_create_transactions(transactions: List[dict]) -> List[dict]:
    """
    Bulk create transactions.
    Returns: List of created transactions.
    """
    print(f"**************************************Bulk creating transactions*************")
    try:
        db = SessionLocal()
        repo = AccountTransactionRepository(db)
        transaction_models = [AccountTransactionModel(**t) for t in transactions]
        db_transactions = [AccountTransactionTable(**t.dict(exclude={"id"})) for t in transaction_models]
        
        created_transactions = repo.bulk_create(db_transactions)
        return [AccountTransactionModel.from_orm(t).dict() for t in created_transactions]
    except Exception as e:
        logger.exception("Failed to bulk create transactions")
        raise e
    finally:
        db.close()

@mcp.tool("save_process_log", description="Save process log. Args: {process_log: ProcessLog}")
def save_process_log(process_log: dict) -> dict:
    """
    Save process log to database.
    """
    print(f"**************************************Saving process log*************")
    try:
        db = SessionLocal()
        repo = ProcessLogRepository(db)
        # Validate input with Pydantic model
        log_model = ProcessLog(**process_log)
        saved_log = repo.save(log_model)
        return {"id": saved_log.id, "status": "saved"}
    except Exception as e:
        logger.exception("Failed to save process log")
        raise e
    finally:
        db.close()


@mcp.tool("query_database", description="Execute a natural language query against the database. Args: {query: str}")
async def query_database(query: str) -> dict:
    """
    Executes a natural language query against the database.
    Returns: Structured answer containing generated SQL, result, and final answer.
    """
    return await service.process_query(query)        

if __name__ == "__main__":
    # Run as streamable-http MCP server (exposes POST /mcp)
    # Ensure you set MCP_SERVER_API_KEY and configure reverse proxy / TLS for production
    # mcp.run(transport="streamable-http")
    uvicorn.run(app)

