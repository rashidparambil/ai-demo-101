# client_mcp_server.py
# MCP server exposing find_client(name: str) -> {id, name, match_score}
import os
import logging
from dotenv import load_dotenv
import uvicorn

# mcp provides a simple way to expose tools
from mcp.server.fastmcp import FastMCP

import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client_mcp_server")

DB_HOST = os.getenv("db_host", "localhost")
DB_PORT = int(os.getenv("db_port", 5432))
DB_NAME = os.getenv("db_name")
DB_USER = os.getenv("db_user")
DB_PASSWORD = os.getenv("db_password")

# Optional simple API key auth for incoming MCP calls (Streamable HTTP supports headers)
MCP_SERVER_API_KEY = os.getenv("MCP_SERVER_API_KEY","")  # set on server and client

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

mcp = FastMCP("client-search-mcp",host="localhost",port=9000)


@mcp.tool("find_client", description="Find client by name. Args: {name: str}")
def find_client(name: str) -> dict:
    """
    Find a client by name.
    Returns: {"id": int, "name": str, "score": float} or raise if not found.
    """
    print(f"**************************************Finding client with name: {name}*************") 
    # Basic normalization + simple LIKE search; replace with your fuzzy logic if desired
    q = name.strip()
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name FROM client WHERE LOWER(name) LIKE LOWER(%s) ORDER BY id LIMIT 1;",
            (f"%{q}%",),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return {"found": False, "message": f"No client matching '{name}'"}
        # Return top match and list of candidates (optional)
        top = rows[0]
        candidates = [{"id": r["id"], "name": r["name"]} for r in rows]
        return {"found": True, "client_id": int(top["id"]), "client_name": top["name"], "candidates": candidates}

    except Exception as e:
        logger.exception("DB lookup failed")
        raise e  # MCP will return tool error to caller


if __name__ == "__main__":
    # Run as streamable-http MCP server (exposes POST /mcp)
    # Ensure you set MCP_SERVER_API_KEY and configure reverse proxy / TLS for production
    mcp.run(transport="streamable-http")
