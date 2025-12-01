import logging
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2.extensions import register_adapter
import json
from config import config


from repository.process_type import ProcessType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientRuleEmbedding:
    def __init__(self, client_id: int):
        """
        Initialize the embedding service for client rules.
        
        Args:
            client_id: Integer ID of the client
        """
        self.client_id = client_id

        # Setup Google Embeddings using unified config
        google_api_key = config.google_api_key
        if not google_api_key:
            raise ValueError("google_api_key not found in config")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=google_api_key
        )

        # Database Configuration from unified config
        self.db_host = config.db_host
        self.db_port = config.db_port
        self.db_name = config.db_name
        self.db_user = config.db_user
        self.db_password = config.db_password

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

    def _parse_embedding(self, embedding_str: str) -> list:
        """
        Parse pgvector embedding string format to list of floats.

        pgvector stores as: "[0.1,0.2,0.3,...]"

        Args:
            embedding_str: String representation from pgvector

        Returns:
            List of floats
        """
        try:
            # pgvector returns as string like "[0.123, 0.456, ...]"
            # Remove brackets and split by comma
            embedding_str = embedding_str.strip('[]')
            embedding_list = [float(x.strip()) for x in embedding_str.split(',')]
            return embedding_list
        except Exception as e:
            logger.error(f"Error parsing embedding: {str(e)}")
            return []

    def store_client_rules(self, process_type: ProcessType, rules: List[str]) -> Dict[str, Any]:
        """
        Store client rules with embeddings in the client_rule table.
        
        Args:
            rules: List of rule strings to store
        
        Returns:
            Dictionary with status and result information
        """
        if not rules:
            logger.warning(f"No rules to store for client {self.client_id}")
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
                (self.client_id, rule, process_type.value, emb)
                for rule, emb in zip(rules, embeddings)
            ]

            # SQL to insert into client_rule table
            sql = """
                INSERT INTO client_rule (client_id, rule_content, process_type, embedding)
                VALUES (%s, %s, %s, %s::vector)
            """

            # Execute batch insert
            logger.info(f"Inserting {len(data)} rules into database...")
            execute_batch(cursor, sql, data, page_size=100)
            
            conn.commit()
            
            logger.info(f"✓ Successfully stored {len(data)} rules for client {self.client_id}")
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "client_id": self.client_id,
                "rules_stored": len(data)
            }

        except Exception as e:
            logger.error(f"Error storing rules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "client_id": self.client_id
            }

    def search_rules(self,process_type: ProcessType, query: str = None, k: int = 3, return_all: bool = False, include_embeddings: bool = False) -> Dict[str, Any]:
        """
        Search for similar rules or retrieve all rules for a client.

        Args:
            process_type: ProcessType enum value to filter rules by process type
            query: Search query string for semantic similarity (optional if return_all=True)
            k: Number of results to return (default: 3)
            return_all: If True, return all rules for the client (ignores query and k)
            include_embeddings: If True, include embedding vectors in response (default: False)

        Returns:
            Dictionary with search results
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if return_all:
                # Return all rules for the client
                logger.info(f"Retrieving all rules for client {self.client_id}")
                
                # Build SQL based on whether embeddings are requested
                if include_embeddings:
                    sql = """
                        SELECT 
                            id,
                            client_id,
                            process_type,
                            rule_content,
                            is_auto_apply,
                            embedding::text
                        FROM client_rule
                        WHERE client_id = %s and process_type = %s
                        ORDER BY id ASC
                    """
                else:
                    sql = """
                        SELECT 
                            id,
                            client_id,
                            process_type,
                            rule_content,
                            is_auto_apply
                        FROM client_rule
                        WHERE client_id = %s and process_type = %s
                        ORDER BY id ASC
                    """
                
                cursor.execute(sql, (self.client_id,process_type))
                results = cursor.fetchall()

                cursor.close()
                conn.close()

                if not results:
                    logger.info(f"No rules found for client {self.client_id}")
                    return {
                        "success": True,
                        "client_id": self.client_id,
                        "results_count": 0,
                        "results": []
                    }

                # Format results based on include_embeddings flag
                if include_embeddings:
                    formatted_results = [
                        {
                            "rule_id": row[0],
                            "client_id": row[1],
                            "process_type": ProcessType(row[2]).name,
                            "rule_content": row[3],
                            "is_auto_apply": row[4],
                            "embedding": self._parse_embedding(row[5])  # Convert pgvector string to list
                        }
                        for row in results
                    ]
                else:
                    formatted_results = [
                        {
                            "rule_id": row[0],
                            "client_id": row[1],
                            "process_type": ProcessType(row[2]).name,
                            "rule_content": row[3],
                            "is_auto_apply": row[4]
                        }
                        for row in results
                    ]

                logger.info(f"Retrieved {len(formatted_results)} rules for client {self.client_id}")

                return {
                    "success": True,
                    "client_id": self.client_id,
                    "include_embeddings": include_embeddings,
                    "results_count": len(formatted_results),
                    "results": formatted_results
                }

            else:
                # Semantic search based on query
                if not query:
                    return {
                        "success": False,
                        "error": "Query is required when return_all=False",
                        "client_id": self.client_id
                    }

                logger.info(f"Searching for rules with query: {query}")
                
                # Generate embedding for query
                query_embedding = self.embeddings.embed_query(query)
                
                # Convert to list if needed
                if hasattr(query_embedding, 'tolist'):
                    query_embedding = query_embedding.tolist()
                elif not isinstance(query_embedding, list):
                    query_embedding = list(query_embedding)

                # Build SQL based on whether embeddings are requested
                if include_embeddings:
                    sql = """
                        SELECT 
                            id,
                            client_id,
                            process_type,
                            rule_content,
                            is_auto_apply,
                            embedding::text,
                            1 - (embedding <=> %s::vector) as similarity_score
                        FROM client_rule
                        WHERE client_id = %s and process_type = %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """
                else:
                    sql = """
                        SELECT 
                            id,
                            client_id,
                            process_type,
                            rule_content,
                            is_auto_apply,
                            1 - (embedding <=> %s::vector) as similarity_score
                        FROM client_rule
                        WHERE client_id = %s and process_type = %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """

                cursor.execute(sql, (json.dumps(query_embedding), self.client_id, json.dumps(query_embedding), k))
                results = cursor.fetchall()

                cursor.close()
                conn.close()

                if not results:
                    logger.info(f"No similar rules found for query: {query}")
                    return {
                        "success": True,
                        "query": query,
                        "client_id": self.client_id,
                        "results_count": 0,
                        "results": []
                    }

                # Format results with similarity scores and optional embeddings
                if include_embeddings:
                    formatted_results = [
                        {
                            "rule_id": row[0],
                            "client_id": row[1],
                            "process_type": ProcessType(row[2]).name,
                            "rule_content": row[3],
                            "is_auto_apply": row[4],
                            "embedding": self._parse_embedding(row[5]),
                            "similarity_score": round(float(row[6]), 4)
                        }
                        for row in results
                    ]
                else:
                    formatted_results = [
                        {
                            "rule_id": row[0],
                            "client_id": row[1],
                            "process_type": ProcessType(row[2]).name,
                            "rule_content": row[3],
                            "is_auto_apply": row[4],
                            "similarity_score": round(float(row[4]), 4)
                        }
                        for row in results
                    ]

                logger.info(f"Found {len(formatted_results)} similar rules for query: {query}")

                return {
                    "success": True,
                    "query": query,
                    "client_id": self.client_id,
                    "include_embeddings": include_embeddings,
                    "results_count": len(formatted_results),
                    "results": formatted_results
                }

        except Exception as e:
            logger.error(f"Error searching rules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "client_id": self.client_id
            }

    def delete_client_rules(self) -> Dict[str, Any]:
        """
        Delete all rules for a client (useful for updates).
        
        Returns:
            Dictionary with status
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM client_rule WHERE client_id = %s"
            cursor.execute(sql, (self.client_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()

            cursor.close()
            conn.close()

            logger.info(f"Deleted {deleted_count} rules for client {self.client_id}")

            return {
                "success": True,
                "client_id": self.client_id,
                "rules_deleted": deleted_count
            }

        except Exception as e:
            logger.error(f"Error deleting rules: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }