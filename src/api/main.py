#from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from genai.extract import Extract

app = FastAPI()

class MailRequest(BaseModel):
    from_address: str
    subject: str
    content: str


@app.post("/process")
def read_item(request: MailRequest):
    pro = Extract()
    response = pro.process(request.content)
    return {"response": response.content }
