from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from api.config import config
import logging
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)

class SQLExecutor:
    def __init__(self):
        self.engine = create_engine(config.database_url)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=config.google_api_key
        )

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

        # Handle EMBEDDING_FUNCTION
        # Regex to find EMBEDDING_FUNCTION('text') or EMBEDDING_FUNCTION("text")
        embedding_pattern = r"EMBEDDING_FUNCTION\((['\"])(.*?)\1\)"
        
        def replace_embedding(match):
            text_content = match.group(2)
            logger.info(f"Generating embedding for: {text_content}")
            vector = self.embeddings.embed_query(text_content)
            return f"'{str(vector)}'"

        # Replace all occurrences
        if "EMBEDDING_FUNCTION" in query:
            query = re.sub(embedding_pattern, replace_embedding, query)
            logger.info("Query with embeddings injected")

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                keys = result.keys()
                return [dict(zip(keys, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {query}. Error: {e}")
            raise e
