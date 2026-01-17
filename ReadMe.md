PreRequsite
#-----------------------------------------
Python version : 3.14

Fast API
Install following packages
    pip install "fastapi[standard]"

Postgresql
    pip install sqlalchemy
    pip install psycopg2-binary
    pip install pgvector

LangChain GenAI
Install following packages
    pip install -U langchain-google-genai


Vector Embeding 

pip install langchain langchain-google-genai langchain-postgres psycopg2-binary


mcp
pip install mcp langchain-mcp-adapters langchain psycopg2-binary python-dotenv requests


#-----------------------------------------
Run Fast Api
    fastapi dev src/api/main.py


Gen AI Test input
Please initiate processing of following from ABC Company.\nABC Company\nJohn Doe, 12064654654, 150, 50, 12/12/2025\nRobert T, 12064654678, 300, 70, 12/12/2025\nDavid  B, 12064657988, 220, 40, 12/12/2025\n3


{
  "from_address": "test@jio-mobile-test.com",
  "subject": "Placement Processing",
  "content": "Please initiate processing of following from Jio Mobile.\nJio Mobile\nJohn Doe, 12064654654, 50, 150, 12/12/2025\nRobert T, 12064654678, 70, 300, 12/12/2025\nDavid  B, 120646, 9, 251, 12/12/2025\n3"
}


{
  "from_address": "test@ai-notts-test.com",
  "subject": "Placement Processing",
  "content": "Please initiate processing of following from Ai Notts.\nAi Notts\nJohn Doe, 12064& 654654, 50, 150, 12/12/2025\nRobert T, 0987654328777, 9, 300, 12/12/2025\nDavid  B, 12064657988, 9, 251, 12/12/2025\n3"
}





# docker build -t ai-demo-101-mcp .
# docker run -d -p 7080:7080 --name ai-demo-101-mcp ai-demo-101-mcp

# docker build -t ai-demo-101-api .
# docker run -d -p 7081:7081 --name ai-demo-101-api ai-demo-101-api