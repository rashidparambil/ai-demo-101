#from typing import Union

from fastapi import FastAPI
from genai.extract import Extract
from repository.routes import router as client_router
from repository.client_rules import rules_router
from repository.models import MailRequest
from config import config
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Log config loaded
logger.info(f"Config loaded: {config}")

app = FastAPI()

# Register the client router
app.include_router(client_router)
app.include_router(rules_router)



# Create Extract instance once (lightweight, no MCP session)
extractor = Extract()

@app.post("/process")
async def read_item(request: MailRequest):
    response = await extractor.process(f"subject={request.subject}\n contnet={request.content}")
    return {"response": response }

