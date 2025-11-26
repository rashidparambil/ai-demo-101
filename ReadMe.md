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

#-----------------------------------------
Run Fast Api
    fastapi dev src/api/main.py


Gen AI Test input
Please initiate processing of following from ABC Company.\nABC Company\nJohn Doe, 12064654654, 150, 50, 12/12/2025\nRobert T, 12064654678, 300, 70, 12/12/2025\nDavid  B, 12064657988, 220, 40, 12/12/2025\n3

