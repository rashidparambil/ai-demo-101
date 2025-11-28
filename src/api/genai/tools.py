from langchain.tools import tool
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@tool
def format_account_number(account_number: str, client: str) -> str:
    """Format account number for client ABC"""
    if client == 'ABC':
        return account_number[:3] + '-' + account_number[3:]
    return account_number

@tool
def check_minium_amount(amount_paid: float, client: str) -> bool:
    """Check minium amount for client ABC"""
    if client == 'ABC' and amount_paid < 10:
        return False
    return True

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content = f"Tool error please check your input{str(e)}",
            tool_call_id=request.tool_call["id"])
