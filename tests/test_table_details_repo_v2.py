import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import MagicMock, patch
from api.chat_bot.table_detail_repository import TableDetailsRepository
from api.chat_bot.models import TableDetails

class TestTableDetailsRepository(unittest.TestCase):
    @patch('api.chat_bot.table_detail_repository.GoogleGenerativeAIEmbeddings')
    def test_add_and_get(self, MockEmbeddings):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock Embeddings
        mock_embeddings = MockEmbeddings.return_value
        mock_embeddings.embed_query.return_value = [0.1] * 3072
        
        repo = TableDetailsRepository(mock_db)
        
        # Test add
        # We pass a string description as per the repository implementation I saw earlier
        # def add(self, table_description: str) -> TableDetails:
        description = "Test Table"
        
        repo.add(description)
        
        mock_embeddings.embed_query.assert_called_with("Test Table")
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called()

if __name__ == '__main__':
    unittest.main()
