#from typing import Union
import sys
from pathlib import Path
# Add src to path so 'api' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from api.genai.extract import Extract
from api.repository.routes import router as client_router
from api.repository.client_rules import rules_router
from api.repository.account_routes import router as account_router
from api.repository.account_transaction_routes import router as transaction_router
from api.chat_bot.routes import router as chat_router
from api.chat_bot.table_detail_routes import router as table_detail_router
from api.repository.models import MailRequest
from api.config import config
from api.repository.final_response import FinalResponse
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Log config loaded
logger.info(f"Config loaded: {config}")

app = FastAPI()

# Register the client router
app.include_router(client_router)
app.include_router(rules_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(chat_router)
app.include_router(table_detail_router)



# Create Extract instance once (lightweight, no MCP session)
extractor = Extract()

@app.post("/process")
async def read_item(request: MailRequest):
    response = await extractor.process(f"subject={request.subject}\n contnet={request.content}")
    #raw_response = response[0]["text"][7:-3] #remove quotes from the start and end for json string
    #json_response: FinalResponse = json.loads(raw_response)

    #Check account exists in database if the process type is Transaction
    #Handle error
    #Write a save method to save valid accounts.
    #Write process log for error record
    #Initiate a response email

    return {"response": response }

