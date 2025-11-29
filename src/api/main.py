#from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from genai.extract import Extract
from repository.routes import router as client_router
from repository.client_rules import rules_router

app = FastAPI()

# Register the client router
app.include_router(client_router)
app.include_router(rules_router)

class MailRequest(BaseModel):
    from_address: str
    subject: str
    content: str

# Create Extract instance once (lightweight, no MCP session)
extractor = Extract()

@app.post("/process")
async def read_item(request: MailRequest):
    response = await extractor.process(request.content)
    return {"response": response }

