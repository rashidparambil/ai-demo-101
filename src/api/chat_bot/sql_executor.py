from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from api.config import config
import logging

logger = logging.getLogger(__name__)

class SQLExecutor:
    def __init__(self):
        self.engine = create_engine(config.database_url)

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a read-only SQL query.
        
        Args:
            query: SQL query to execute.
            
        Returns:
            List of dictionaries representing the result rows.
        """
        # Basic safety check (should be handled by database permissions ideally)
        forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]
        if any(keyword in query.upper() for keyword in forbidden_keywords):
            raise ValueError("Only read-only queries are allowed.")

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                keys = result.keys()
                return [dict(zip(keys, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {query}. Error: {e}")
            raise e
