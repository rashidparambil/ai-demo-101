from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from api.config import config
from api.chat_bot.models import TableDetailsTable, TableDetails
import logging

logger = logging.getLogger(__name__)

class TableDetailsRepository:
    def __init__(self, db: Session):
        self.db = db
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=config.google_api_key
        )

    def add(self, table_description: str) -> TableDetails:
        """
        Add a new table detail with embedding generation.
        """
        try:
            # Generate embedding
            embedding = self.embeddings.embed_query(table_description)
            
            db_item = TableDetailsTable(
                table_description=table_description,
                embedding=embedding
            )
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            return TableDetails.model_validate(db_item)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding table details: {e}")
            raise e

    def get_all(self) -> List[TableDetails]:
        """
        Get all table details.
        """
        try:
            stmt = select(TableDetailsTable)
            results = self.db.execute(stmt).scalars().all()
            return [TableDetails.model_validate(r) for r in results]
        except Exception as e:
            logger.error(f"Error getting all table details: {e}")
            raise e

    def get_by_id(self, id: int) -> Optional[TableDetails]:
        """
        Get table detail by ID.
        """
        try:
            item = self.db.get(TableDetailsTable, id)
            if item:
                return TableDetails.model_validate(item)
            return None
        except Exception as e:
            logger.error(f"Error getting table detail by id {id}: {e}")
            raise e

    def delete(self, id: int) -> bool:
        """
        Delete table detail by ID.
        """
        try:
            item = self.db.get(TableDetailsTable, id)
            if item:
                self.db.delete(item)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting table detail {id}: {e}")
            raise e

    def search(self, query: str, limit: int = 5) -> List[TableDetails]:
        """
        Semantic search for table details.
        """
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            # Use pgvector's l2_distance or cosine_distance
            # Here we use the <=> operator which is cosine distance in pgvector (or l2 depending on index, but usually cosine for embeddings)
            # Actually <=> is cosine distance, <-> is L2 distance, <#> is inner product
            # For similarity search, we usually want closest items.
            
            stmt = select(TableDetailsTable).order_by(
                TableDetailsTable.embedding.l2_distance(query_embedding)
            ).limit(limit)
            
            results = self.db.execute(stmt).scalars().all()
            return [TableDetails.model_validate(r) for r in results]
        except Exception as e:
            logger.error(f"Error searching table details: {e}")
            raise e
