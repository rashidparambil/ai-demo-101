import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from .tools import format_account_number, check_minium_amount, handle_tool_errors

class Extract:
    system_message = "You are a helpful assistant that extract Customer Name, Customer Account, Amount Paid, Balance Amount form the message and return as a object or list of objects. Use format_account_number and check_minium_amount tools to support this task"
    def __init__(self):
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("google_api_key")
        # ✅ Step 1: Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_retries=1,
            google_api_key=GOOGLE_API_KEY
        )
        self.system_message = "You are a helpful assistant that extract Customer Name, Customer Account, Amount Paid, Balance Amount form the message and return as a object or list of objects. Use format_account_number and check_minium_amount tools to support this task"
        self.agent = create_agent(llm, tools=[format_account_number, check_minium_amount], system_prompt = self.system_message)


    def process(self, message: str):
        ai_msg = self.agent.invoke({"messages": [{"role": "user", "content": message}]})
        return ai_msg