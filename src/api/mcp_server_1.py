# client_mcp_server.py
# MCP server exposing find_client(name: str) -> {id, name, match_score}
from config import config
import logging
# from dotenv import load_dotenv
import uvicorn
from repository.client_rule_embedding import ClientRuleEmbedding

# mcp provides a simple way to expose tools
from mcp.server.fastmcp import FastMCP

import psycopg2
from psycopg2.extras import RealDictCursor

# load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client_mcp_server")

# DB_HOST = os.getenv("db_host", "localhost")
# DB_PORT = int(os.getenv("db_port", 5432))
# DB_NAME = os.getenv("db_name")
# DB_USER = os.getenv("db_user")
# DB_PASSWORD = os.getenv("db_password")

# Optional simple API key auth for incoming MCP calls (Streamable HTTP supports headers)
# MCP_SERVER_API_KEY = os.getenv("MCP_SERVER_API_KEY","")  # set on server and client

def get_db_conn():
    return psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        database=config.db_name,
        user=config.db_user,
        password=config.db_password,
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
    
@mcp.tool("find_all_client_rule_by_client_id_and_process_type", description="Find client rules by client Id. Args: {client_id: int, process_type: int}")
def find_all_client_rule_by_client_id(client_id: int, process_type: int) -> dict:
    """
    Find a client rule by client_id.
    Returns: [{"id": int, "rule_content": str, "score": float}] or raise if not found.
    """
    print(f"**************************************Finding client rule by client Id: {client_id}, process_type: {process_type}*************") 
    # Basic normalization + simple LIKE search; replace with your fuzzy logic if desired
    try:
        clientRuleEmbedding = ClientRuleEmbedding(client_id)
        data = clientRuleEmbedding.search_rules(process_type,return_all=True, k=100,include_embeddings=False)
        # # 2. Filter the 'results' list
        # filtered_results = [
        #     item for item in data['results'] 
        #     if item['process_type'] == 'Placement'
        # ]

        # # 3. (Optional) Create a new dictionary with the filtered results
        # filtered_data = {
        #     "success": True,
        #     "client_id": data['client_id'],
        #     "include_embeddings": data['include_embeddings'],
        #     "results_count": len(filtered_results), # Update the count
        #     "results": filtered_results
        # }
        return data

    except Exception as e:
        logger.exception("DB client rule lookup failed")
        raise e  # MCP will return tool error to caller




if __name__ == "__main__":
    # Run as streamable-http MCP server (exposes POST /mcp)
    # Ensure you set MCP_SERVER_API_KEY and configure reverse proxy / TLS for production
    mcp.run(transport="streamable-http")
