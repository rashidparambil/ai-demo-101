import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

class Extract:
    
    def __init__(self):
        load_dotenv()
        GOOGLE_API_KEY = os.getenv("google_api_key")


        # ✅ Step 1: Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_retries=1,
            google_api_key=GOOGLE_API_KEY
        )



    def process(self, message: str):
        messages = [
            (
                "system",
                "You are a helpful assistant that extract Customer Name, Customer Account, Balance Amount form the message and return as a object or list of objects."
            ),
            ("human", message)
        ]
        ai_msg = self.llm.invoke(messages)
        return ai_msg