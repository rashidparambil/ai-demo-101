import os
import asyncio
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from .tools import format_account_number, check_minium_amount

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

class Extract:
    def __init__(self):
        """Initialize without creating MCP session (do it per-request instead)."""
        load_dotenv()
        self.MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9000/mcp")
        self.GOOGLE_API_KEY = os.getenv("google_api_key")
        
        self.system_message = self.system_message = '''
        You are a highly efficient **Data Extraction and Validation Assistant** specializing in financial records.

        **MANDATORY WORKFLOW:**
        1. **Client Verification (REQUIRED):**
        - Extract the client name from the user message
        - Call `find_client(name=...)` to verify the client exists
        - If client not found, STOP and return error

        2. **Rule Retrieval (REQUIRED - DO NOT SKIP):**
        - After client is verified, IMMEDIATELY call `find_all_client_rule_by_client_id(client_id=...)` with the returned client_id
        - This is MANDATORY before any other processing

        3. **Data Extraction:**
        - Extract: Customer Name, Customer Account, Amount Paid, Balance Amount
        - Call `format_account_number(account_number=...)` to validate account
        - Call `check_minium_amount(amount=...)` to validate amount against rules

        4. **Output:**
        - Return JSON object with:
            * client_id
            * client_name
            * extracted_fields
            * validation_results
            * errors (if any)

        **CRITICAL RULE:** You MUST call `find_all_client_rule_by_client_id` after `find_client`. Do not proceed without it.
        '''
     
    async def process(self, message: str):
        """Create agent with fresh MCP session for this request."""
        mcp_servers = {
            "client_mcp": {
                "transport": "streamable_http",
                "url": self.MCP_SERVER_URL
            }
        }

        client = MultiServerMCPClient(mcp_servers)
        
        # Create fresh session for this request
        async with client.session("client_mcp") as session:
            mcptools = await load_mcp_tools(session)

            combined_tools = [format_account_number, check_minium_amount] + mcptools

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.7,
                max_retries=1,
                google_api_key=self.GOOGLE_API_KEY
            )

            agent = create_agent(llm, tools=combined_tools, system_prompt=message)
            
            # Use the agent within the session context
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]}
            )
            
            return result

