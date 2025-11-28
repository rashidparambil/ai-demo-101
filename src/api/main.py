#from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from genai.extract import Extract
from companies.routes import router as companies_router
from companies.company_rules import rules_router

app = FastAPI()

# Register the companies router
app.include_router(companies_router)
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

