import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from api.chat_bot.service import ChatBotService

class TestChatBot(unittest.IsolatedAsyncioTestCase):
    @patch('api.chat_bot.sql_generator.TableDetailsRepository')
    @patch('api.chat_bot.sql_generator.SessionLocal')
    @patch('api.chat_bot.service.SQLExecutor')
    @patch('api.chat_bot.service.ChatGoogleGenerativeAI')
    @patch('api.chat_bot.service.ChatPromptTemplate')
    @patch('api.chat_bot.sql_generator.ChatGoogleGenerativeAI')
    @patch('api.chat_bot.sql_generator.ChatPromptTemplate')
    async def test_process_query(self, MockGenPrompt, MockGenLLM, MockServicePrompt, MockServiceLLM, MockExecutor, MockSession, MockRepo):
        # Mock Repo Search
        mock_db = MagicMock()
        MockSession.return_value = mock_db
        mock_repo = MockRepo.return_value
        
        mock_detail = MagicMock()
        mock_detail.table_description = "CREATE TABLE account ..."
        mock_repo.search.return_value = [mock_detail]
        
        # Mock Generator LLM
        mock_gen_llm = MockGenLLM.return_value
        mock_gen_llm.ainvoke = AsyncMock(return_value=MagicMock(content="SELECT * FROM account"))
        
        mock_gen_chain = MagicMock()
        mock_gen_chain.ainvoke = AsyncMock(return_value=MagicMock(content="SELECT * FROM account"))
        MockGenPrompt.from_template.return_value.__or__.return_value = mock_gen_chain
        
        # Mock Executor
        mock_executor = MockExecutor.return_value
        mock_executor.execute_query.return_value = [{"id": 1, "account_name": "Test Account"}]
        
        # Mock Service LLM
        mock_service_llm = MockServiceLLM.return_value
        mock_service_llm.ainvoke = AsyncMock(return_value=MagicMock(content="The account name is Test Account."))
        
        mock_service_chain = MagicMock()
        mock_service_chain.ainvoke = AsyncMock(return_value=MagicMock(content="The account name is Test Account."))
        MockServicePrompt.from_template.return_value.__or__.return_value = mock_service_chain

        # Initialize service
        service = ChatBotService()
        
        # Test process_query
        response = await service.process_query("What is the account name?")
        
        self.assertEqual(response, "The account name is Test Account.")
        mock_repo.search.assert_called()
        mock_executor.execute_query.assert_called()

if __name__ == '__main__':
    # Since unittest doesn't support async tests natively in older versions, we might need a runner
    # But for simplicity, let's just run the async method manually or use IsolatedAsyncioTestCase if available
    # Or just mock the async calls to be synchronous if we weren't using async/await in the service (but we are)
    
    # Let's try running with asyncio.run
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    test = TestChatBot()
    # We need to manually setup mocks because setUp is not async
    # Actually, let's just use a simple script instead of unittest for async ease here
    pass

# Simple async test script
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from api.chat_bot.service import ChatBotService

async def run_test():
    with patch('api.chat_bot.sql_generator.TableDetailsRepository') as MockRepo, \
         patch('api.chat_bot.sql_generator.SessionLocal') as MockSession, \
         patch('api.chat_bot.service.SQLExecutor') as MockExecutor, \
         patch('api.chat_bot.service.ChatGoogleGenerativeAI') as MockServiceLLM, \
         patch('api.chat_bot.sql_generator.ChatGoogleGenerativeAI') as MockGenLLM:
        
        # Mock Repo
        mock_db = MagicMock()
        MockSession.return_value = mock_db
        mock_repo = MockRepo.return_value
        mock_detail = MagicMock()
        mock_detail.table_description = "CREATE TABLE account ..."
        mock_repo.search.return_value = [mock_detail]
        
        # Mock Generator LLM (we need to mock the chain execution inside generate_sql)
        # Since we can't easily mock the pipe in the class without patching the property or class
        # We will patch the ainvoke of the chain.
        # But wait, the chain is created in __init__.
        # Let's mock the SQLGenerator instance method instead for simplicity in this script
        # OR better, let's trust the unit test class above which mocks properly.
        pass

if __name__ == "__main__":
    # Run the unittest class
    unittest.main()
