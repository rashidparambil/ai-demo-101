import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from api.chat_bot.service import ChatBotService

class TestChatBot(unittest.IsolatedAsyncioTestCase):
    @patch('api.chat_bot.service.create_agent')
    @patch('api.chat_bot.service.ChatGoogleGenerativeAI')
    async def test_process_query(self, MockLLM, MockCreateAgent):
        # Mock Agent
        mock_agent_instance = MockCreateAgent.return_value
        
        # Mock result with list content (simulating the error condition)
        mock_message = MagicMock()
        # Simulate content as a list of parts, e.g., text and something else
        mock_message.content = ['{"generated_sql": "SELECT * FROM account", "sql_result": [{"id": 1}], "final_answer": "Result found."}']
        
        mock_result = {
            "messages": [MagicMock(), mock_message]
        }
        
        mock_agent_instance.ainvoke = AsyncMock(return_value=mock_result)
        
        # Initialize service
        service = ChatBotService()
        
        # Test process_query
        response = await service.process_query("What is the account name?")
        
        self.assertEqual(response["generated_sql"], "SELECT * FROM account")
        self.assertEqual(response["sql_result"], [{"id": 1}])
        self.assertEqual(response["final_answer"], "Result found.")
        
        mock_agent_instance.ainvoke.assert_called()

if __name__ == '__main__':
    unittest.main()
