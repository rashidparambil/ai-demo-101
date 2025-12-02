import unittest
from unittest.mock import MagicMock
from api.repository.account import AccountRepository, Account

class TestAccountRepository(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.repo = AccountRepository(self.mock_db)

    def test_get_by_account_number(self):
        mock_account = Account(id=1, account_number="12345")
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_account
        
        result = self.repo.get_by_account_number("12345")
        
        self.assertEqual(result, mock_account)
        # Verify query construction
        # Note: mocking SQLAlchemy query chains is verbose, mainly checking method existence and basic return

    def test_get_by_account_numbers(self):
        mock_accounts = [Account(id=1, account_number="12345"), Account(id=2, account_number="67890")]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_accounts
        
        result = self.repo.get_by_account_numbers(["12345", "67890"])
        
        self.assertEqual(result, mock_accounts)

if __name__ == '__main__':
    unittest.main()
