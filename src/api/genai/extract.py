import os
import asyncio
from dotenv import load_dotenv
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from api.genai.tools import remove_space_sepcial_chars_from_account_number, check_negative_balance_amount, validate_subject
from api.repository.models import MailRequest

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

class Extract:
    def __init__(self):
        """Initialize without creating MCP session (do it per-request instead)."""
        load_dotenv()
        self.MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://mcp-server-1-489053910225.us-central1.run.app/mcp")
        self.GOOGLE_API_KEY = os.getenv("google_api_key")
        
        self.system_message = '''
            You are a highly efficient **Data Extraction and Validation Assistant** specializing in financial records.
            Your input will be a JSON object containing 'subject' and 'content' fields.

            **MANDATORY WORKFLOW:**

            1. **Subject Validation (REQUIRED - DO NOT SKIP):**
               - Call `validate_subject(subject=...)` with the subject from the input JSON.
               - Check the response. If "valid" is false, IMMEDIATELY STOP and return: `{"error": "<message from tool>"}`
               - If valid, note the process_type returned.

            2. **Client Verification (REQUIRED - DO NOT SKIP):**
               - Extract the client name from the 'content' field (first row of data after intro text).
               - Call `find_client(name=...)` to verify the client exists.
               - If not found, IMMEDIATELY STOP and return: `{"error": "Client verification failed: Client not found."}`

            3. **Rule Retrieval (REQUIRED - DO NOT SKIP):**
               - Call `find_all_client_rule_by_client_id(client_id=..., process_type=...)` 
               - Use the client_id from Step 2 and process_type from Step 1.

            4. **APPLY VALIDATION RULES TO EACH RECORD (CRITICAL):**
       
               For EVERY record extracted in Step 4:
   
                For EVERY field in that record (customer_name, customer_account, amount_paid, balance_amount):
                
                    a) Find all rules for that field from Step 3 where is_auto_apply is True. 

                    b) Execute tools that match the rule where ia_auto_apply is False.

                    c) Do not apply other rules except.
                    
                    d) Apply rules IN THIS ORDER:
                        - First: Apply all TRANSFORMATION rules (strip whitespace, format, etc.)
                        * Use transformed value for subsequent validations
                        - Then: Apply all VALIDATION rules (required, max_length, min_length, etc.)
                        * Use the transformed value to check validations
                    
                    e) Document each rule:
                        - rule_id
                        - rule_type (required, strip, max_length, min_length, etc.)
                        - description
                        - status (pass, fail, applied, skipped, error)
                        - additional details (length, max_length, min_length, error message, etc.)
                    
                    f) Use the TRANSFORMED value as the final field value in extracted_fields
                            

            **Final Output:**
                Return a single comprehensive JSON object:
                
                {
                    "client_id": "...",
                    "client_name": "...",
                    "process_type": 1 or 2,
                    "extracted_fields": [
                    {
                        "customer_name": "FINAL_VALUE_AFTER_ALL_TRANSFORMATIONS",
                        "customer_account": "FINAL_VALUE_AFTER_ALL_TRANSFORMATIONS",
                        "amount_paid": "FINAL_VALUE",
                        "balance_amount": "FINAL_VALUE",
                        "field_validations": {
                        "customer_name": {
                            "rule_1": {
                            "rule_id": 1,
                            "rule_type": "strip",
                            "description": "Remove leading/trailing whitespace",
                            "status": "applied",
                            "original_value": "  John Doe  ",
                            "transformed_value": "John Doe"
                            },
                            "rule_2": {
                            "rule_id": 2,
                            "rule_type": "required",
                            "description": "Customer name is required",
                            "status": "pass",
                            "value": "John Doe",
                            "is_empty": false
                            },
                            "rule_3": {
                            "rule_id": 3,
                            "rule_type": "max_length",
                            "description": "Customer name max 100 characters",
                            "status": "pass",
                            "value": "John Doe",
                            "actual_length": 8,
                            "max_length": 100
                            }
                        },
                        "customer_account": { ... },
                        "amount_paid": { ... },
                        "balance_amount": { ... }
                        }
                    },
                    { ... next record ... }
                    ],
                    "errors": []
                }

                **CRITICAL RULES TO FOLLOW:**

                - Do NOT skip any fields or rules
                - Apply transformations BEFORE validations
                - Use transformed values for all subsequent operations
                - Document EVERY rule application with status
                - If a field fails validation, still include it in output with status "fail"
                - Include only one final extracted_fields array
                - If ANY step fails (subject, client, rules), return error JSON immediately and STOP
                - Return ONLY valid JSON, nothing else
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

            combined_tools = [remove_space_sepcial_chars_from_account_number, check_negative_balance_amount, validate_subject] + mcptools

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                max_retries=1,
                google_api_key=self.GOOGLE_API_KEY
            )

            agent = create_agent(llm, tools=combined_tools, system_prompt=self.system_message)
            
            # Use the agent within the session context
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]}
            )
            
            return result

