from langchain_core.tools import tool
from api.chat_bot.table_detail_repository import TableDetailsRepository
from api.repository.database import SessionLocal
from api.chat_bot.sql_executor import SQLExecutor
from typing import List, Dict, Any

@tool
def search_table_details_tool(query: str) -> List[Dict[str, Any]]:
    """
    Search for relevant table schemas based on a natural language query.
    Use this tool to find out which tables and columns are available to answer the user's question.
    """
    db = SessionLocal()
    try:
        repo = TableDetailsRepository(db)
        results = repo.search(query, limit=5)
        return [
            {
                "table_description": item.table_description,
                "id": item.id
            } 
            for item in results
        ]
    finally:
        db.close()

@tool
def execute_sql_tool(sql_query: str) -> List[Dict[str, Any]]:
    """
    Execute a SQL SELECT query against the database.
    Input should be a valid SQL SELECT statement.
    Returns the query results as a list of dictionaries.
    """
    if not sql_query.strip().upper().startswith("SELECT"):
        return [{"error": "Only SELECT queries are allowed."}]
    
    executor = SQLExecutor()
    try:
        return executor.execute_query(sql_query)
    except Exception as e:
        return [{"error": str(e)}]
