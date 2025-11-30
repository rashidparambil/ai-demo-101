from langchain.tools import tool
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@tool
def format_account_number(account_number: str, client: str) -> str:
    """Format account number for client ABC"""
    if client == 'Jio Mobile':
        return account_number[:3] + '-' + account_number[3:]
    return account_number

@tool
def check_minium_amount(amount_paid: float, minum_amount: float, content_rule: str) -> bool:
    """Check minium amount for client"""
    print(f"content_rule: {content_rule}, minum_amount: {minum_amount}")
    if(minum_amount == 0):
        return True
    return amount_paid < minum_amount


@tool("validate_subject", description="Validate and identify the process type from the subject line. Args: {subject: str}")
def validate_subject(subject: str) -> dict:
    """
    Validate and identify the process type from the subject line.
    
    Returns a dict with process_type (1 for Placement, 2 for Transaction) 
    or an error if subject doesn't match required keywords.
    
    Args:
        subject: The email subject line to validate
    """
    subject_lower = subject.lower()
    
    if "placement" in subject_lower:
        return {
            "valid": True,
            "process_type": 1,
            "message": f"Subject '{subject}' matched 'Placement', ProcessType set to 1"
        }
    elif "Transaction" in subject_lower:
        return {
            "valid": True,
            "process_type": 2,
            "message": f"Subject '{subject}' matched 'Transaction', ProcessType set to 2"
        }
    else:
        return {
            "valid": False,
            "process_type": None,
            "message": "ProcessType not identified from subject. Subject must contain 'Placement' or 'Transaction'."
        }

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content = f"Tool error please check your input{str(e)}",
            tool_call_id=request.tool_call["id"])
