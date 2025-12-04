import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import MagicMock, patch
from api.chat_bot.mcp import search_table_details
from api.chat_bot.models import TableDetails

class TestMCPSearch(unittest.TestCase):
    @patch('api.chat_bot.mcp.SessionLocal')
    @patch('api.chat_bot.mcp.TableDetailsRepository')
    def test_search_table_details(self, MockRepo, MockSession):
        mock_db = MagicMock()
        MockSession.return_value = mock_db
        mock_repo = MockRepo.return_value
        
        # Mock search result
        mock_detail = TableDetails(id=1, table_description="Test Table", embedding=[0.1]*3072)
        mock_repo.search.return_value = [mock_detail]
        
        results = search_table_details("query")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['table_description'], "Test Table")
        mock_repo.search.assert_called_with("query", 5)
        mock_db.close.assert_called()

if __name__ == '__main__':
    unittest.main()
