from mcp.server.fastmcp import FastMCP
from api.chat_bot.service import ChatBotService
from api.chat_bot.table_detail_repository import TableDetailsRepository
from api.repository.database import SessionLocal
import asyncio

# Create a separate MCP server instance for chat bot or reuse existing one
# The user asked for "all the method should in chat-boat folder"
# But MCP server usually runs as a standalone script or attached to FastAPI
# I'll create a standalone MCP definition here that can be imported or run

mcp = FastMCP("chat_bot")
service = ChatBotService()

@mcp.tool("chat_with_db", description="Chat with the database using natural language. Args: {query: str}")
async def chat_with_db(query: str) -> dict:
    """
    Chat with the database.
    Returns: Structured answer containing generated SQL, result, and final answer.
    """
    return await service.process_query(query)

@mcp.tool("search_table_details", description="Search table details by semantic similarity. Args: {query: str, limit: int}")
def search_table_details(query: str, limit: int = 5) -> list[dict]:
    """
    Search table details by semantic similarity.
    Returns: List of table details.
    """
    try:
        db = SessionLocal()
        repo = TableDetailsRepository(db)
        results = repo.search(query, limit)
        return [item.model_dump() for item in results]
    except Exception as e:
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
