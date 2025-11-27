import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2.extensions import register_adapter
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompanyRuleEmbedding:
    def __init__(self, company_id: int):
        """
        Initialize the embedding service for company rules.
        
        Args:
            company_id: Integer ID of the company
        """
        self.company_id = company_id

        # Load environment variables
        load_dotenv()
        
        # Setup Google Embeddings
        google_api_key = os.getenv("google_api_key")
        if not google_api_key:
            raise ValueError("google_api_key not found in environment variables")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=google_api_key

        )

        # Database Configuration
        self.db_host = os.getenv("db_host", "localhost")
        self.db_port = int(os.getenv("db_port", "5432"))
        self.db_name = os.getenv("db_name")
        self.db_user = os.getenv("db_user")
        self.db_password = os.getenv("db_password")

    def _get_connection(self):
        """Create and return a database connection."""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def store_company_rules(self, rules: List[str]) -> Dict[str, Any]:
        """
        Store company rules with embeddings in the company_rule table.
        
        Args:
            rules: List of rule strings to store
        
        Returns:
            Dictionary with status and result information
        """
        if not rules:
            logger.warning(f"No rules to store for company {self.company_id}")
            return {
                "success": False,
                "error": "No rules provided"
            }

        try:
            # Generate embeddings for all rules at once (batch)
            logger.info(f"Generating embeddings for {len(rules)} rules...")
            embeddings = self.embeddings.embed_documents(rules)
            
            if not embeddings:
                raise ValueError("Failed to generate embeddings")

            # Convert embeddings to lists (psycopg2 compatible format)
            # Google embeddings are already lists, but ensure they are
            embeddings = [
                emb.tolist() if hasattr(emb, 'tolist') else list(emb) if isinstance(emb, (list, tuple)) else emb
                for emb in embeddings
            ]

            # Connect to database
            conn = self._get_connection()
            cursor = conn.cursor()

            # Prepare data for batch insert
            # pgvector expects format: [0.1, 0.2, ..., 0.768]
            data = [
                (self.company_id, rule, emb)
                for rule, emb in zip(rules, embeddings)
            ]

            # SQL to insert into company_rule table
            sql = """
                INSERT INTO company_rule (company_id, rule_content, embedding)
                VALUES (%s, %s, %s::vector)
            """

            # Execute batch insert
            logger.info(f"Inserting {len(data)} rules into database...")
            execute_batch(cursor, sql, data, page_size=100)
            
            conn.commit()
            
            logger.info(f"✓ Successfully stored {len(data)} rules for company {self.company_id}")
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "company_id": self.company_id,
                "rules_stored": len(data)
            }

        except Exception as e:
            logger.error(f"Error storing rules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "company_id": self.company_id
            }

    def search_rules(self, query: str, k: int = 3) -> Dict[str, Any]:
        """
        Search for similar rules using vector similarity (cosine distance).
        
        Args:
            query: Search query string
            k: Number of results to return (default: 3)
        
        Returns:
            Dictionary with search results
        """
        try:
            logger.info(f"Searching for rules with query: {query}")
            
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Convert to list if needed
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            elif not isinstance(query_embedding, list):
                query_embedding = list(query_embedding)

            # Connect to database
            conn = self._get_connection()
            cursor = conn.cursor()

            # SQL query using pgvector cosine distance operator (<=>)
            # <=> computes cosine distance (smaller = more similar)
            sql = """
                SELECT 
                    id,
                    company_id,
                    rule_content,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM company_rule
                WHERE company_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """

            cursor.execute(sql, (json.dumps(query_embedding), self.company_id, json.dumps(query_embedding), k))
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            if not results:
                logger.info(f"No similar rules found for query: {query}")
                return {
                    "success": True,
                    "query": query,
                    "company_id": self.company_id,
                    "results_count": 0,
                    "results": []
                }

            # Format results
            formatted_results = [
                {
                    "rule_id": row[0],
                    "company_id": row[1],
                    "rule_content": row[2],
                    "similarity_score": round(float(row[3]), 4)
                }
                for row in results
            ]

            logger.info(f"Found {len(formatted_results)} similar rules")

            return {
                "success": True,
                "query": query,
                "company_id": self.company_id,
                "results_count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            logger.error(f"Error searching rules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "company_id": self.company_id
            }

    def delete_company_rules(self) -> Dict[str, Any]:
        """
        Delete all rules for a company (useful for updates).
        
        Returns:
            Dictionary with status
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM company_rule WHERE company_id = %s"
            cursor.execute(sql, (self.company_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()

            cursor.close()
            conn.close()

            logger.info(f"Deleted {deleted_count} rules for company {self.company_id}")

            return {
                "success": True,
                "company_id": self.company_id,
                "rules_deleted": deleted_count
            }

        except Exception as e:
            logger.error(f"Error deleting rules: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }