import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import MagicMock, patch
from api.chat_bot.repository import TableDetailsRepository
from api.chat_bot.models import TableDetails

class TestTableDetailsRepository(unittest.TestCase):
    @patch('api.chat_bot.repository.GoogleGenerativeAIEmbeddings')
    def test_add_and_get(self, MockEmbeddings):
        # Mock DB session
        mock_db = MagicMock()
        
        # Mock Embeddings
        mock_embeddings = MockEmbeddings.return_value
        mock_embeddings.embed_query.return_value = [0.1] * 768
        
        repo = TableDetailsRepository(mock_db)
        
        # Test add
        details = TableDetails(table_description="Test Table")
        
        # Mock db.add and db.commit
        mock_db_item = MagicMock()
        mock_db_item.id = 1
        mock_db_item.table_description = "Test Table"
        mock_db_item.embedding = [0.1] * 768
        
        # When we add, we expect it to return the model
        # But in the real code, we create a TableDetailsTable object
        # We need to mock the return of TableDetails.model_validate(db_item)
        # Or just trust the logic if we mock the db interactions correctly
        
        # Let's mock the repo.add method's internal behavior slightly by mocking TableDetailsTable constructor?
        # No, better to test the logic.
        
        # Since we can't easily mock the SQLAlchemy model instantiation and return it from db.add
        # without a real DB or complex mocking, let's focus on interactions.
        
        repo.add(details)
        
        mock_embeddings.embed_query.assert_called_with("Test Table")
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called()

    @patch('api.chat_bot.repository.GoogleGenerativeAIEmbeddings')
    def test_search(self, MockEmbeddings):
        mock_db = MagicMock()
        mock_embeddings = MockEmbeddings.return_value
        mock_embeddings.embed_query.return_value = [0.1] * 768
        
        repo = TableDetailsRepository(mock_db)
        
        # Mock execute result
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.table_description = "Found Table"
        mock_row.embedding = [0.1] * 768
        
        mock_result.scalars.return_value.all.return_value = [mock_row]
        mock_db.execute.return_value = mock_result
        
        results = repo.search("query")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].table_description, "Found Table")
        mock_embeddings.embed_query.assert_called_with("query")

if __name__ == '__main__':
    unittest.main()
