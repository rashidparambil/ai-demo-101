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
        
        self.system_message = '''You are a helpful assistant that extract Customer Name,
                                 Customer Account, Amount Paid, Balance Amount form the message and return as a object or list of objects. 
                                 verify the client that is provided in first row in user query by calling `find_client(name=...) and return Client name nad Client Id. provide not found error if not able to find`. 
                                 Use format_account_number and check_minium_amount tools to support this task'''
     
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

