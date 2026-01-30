# Model Context Protocol (MCP) Demo

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io/)

A real-world demo: Connect your MCP-enabled API to Claude Desktop and seamlessly integrate with third-party tools.

---

## What is MCP?

MCP (Model Context Protocol) is a standardized way to expose tools and data to AI assistants like Claude Desktop. It allows safe, auditable integrations between your backend services and AI hosts.

## When to Use MCP

- Context injection (give the model controlled access to private docs/databases).
- Tool execution (send messages, trigger workflows, update systems).
- Reusable integrations across multiple AI hosts and assistants.

## Architecture

Components:
- **MCP Host**: The assistant UI or platform (Claude Desktop).
- **MCP Client**: Protocol implementation inside the host.
- **MCP Server**: Your service exposing tools/resources.
- **Local/Remote Tool**: Downstream systems (APIs, DBs, files).

Flow: Host → MCP Client → MCP Server → Tool → MCP Server → Host.

## Demo — Claude Desktop → MCP → Third-Party API

Showcases Claude Desktop invoking an MCP-enabled API that queries a third-party service.

**High-level flow:**
1. Claude recognizes an intent and calls the MCP Client.
2. MCP Client invokes your MCP Server with a structured payload.
3. MCP Server validates, applies policies, and forwards to a connector.
4. Connector calls the third-party API and returns a sanitized response.
5. MCP Server audits the call and responds to Claude.

## Prerequisites

- Claude Desktop installed
- Network access to `http://localhost:7080/mcp`

## Quick Start

### 1. Configure Claude Desktop

Edit `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "ai_demo_mcp": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:7080/mcp"
      ]
    }
  }
}
```

### 2. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

### 3. Try Demo Queries

Ask Claude questions like:

```
Show me all accounts with transactions over $500
```

```
Which clients have the highest unpaid fees?
```

## Available Tools

| Tool | Description |
|------|-------------|
| `find_client` | Find a client by name |
| `find_all_client_rule_by_client_id_and_process_type` | Get rules for a client |
| `get_all_accounts` | List all accounts |
| `get_all_transactions` | List all transactions |
| `query_database` | Execute natural language queries |
| `save_accounts_and_transactions` | Save account/transaction data |
| `accounts_urc_check` | Validate unrecognized accounts |

---

**Questions?** Check the [MCP Documentation](https://modelcontextprotocol.io/)
```

