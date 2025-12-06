import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import MagicMock, patch
from api.mcp_server_1 import get_all_accounts, bulk_create_accounts, get_all_transactions, bulk_create_transactions
from api.repository.models import Account, AccountTransaction
from decimal import Decimal

class TestMCPServer(unittest.TestCase):
    @patch('api.mcp_server_1.SessionLocal')
    @patch('api.mcp_server_1.AccountRepository')
    def test_get_all_accounts(self, MockRepo, MockSession):
        mock_db = MagicMock()
        MockSession.return_value = mock_db
        mock_repo = MockRepo.return_value
        
        # Mock return value
        mock_account = MagicMock()
        mock_account.id = 1
        mock_account.client_id = 1
        mock_account.account_name = "Test Account"
        mock_account.account_number = "12345"
        mock_account.account_balance = Decimal("100.00")
        mock_account.account_fee_balance = Decimal("0.00")
        mock_account.correlation_id = None
        
        mock_repo.list.return_value = [mock_account]
        
        result = get_all_accounts()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['account_number'], "12345")
        mock_repo.list.assert_called_once()

    @patch('api.mcp_server_1.SessionLocal')
    @patch('api.mcp_server_1.AccountTransactionRepository')
    def test_get_all_transactions(self, MockRepo, MockSession):
        mock_db = MagicMock()
        MockSession.return_value = mock_db
        mock_repo = MockRepo.return_value
        
        mock_tx = MagicMock()
        mock_tx.id = 1
        mock_tx.account_id = 1
        mock_tx.transaction_amount = Decimal("50.00")
        mock_tx.fee_amount = Decimal("1.00")
        mock_tx.correlation_id = None
        
        mock_repo.list.return_value = [mock_tx]
        
        result = get_all_transactions()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['transaction_amount'], Decimal("50.00"))

if __name__ == '__main__':
    unittest.main()
