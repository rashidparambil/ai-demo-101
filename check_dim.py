from langchain_google_genai import GoogleGenerativeAIEmbeddings
from api.config import config
import os

# Mock config if needed or rely on env vars loaded by api.config
# Assuming api.config loads correctly as verified before

def check_dimension():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=config.google_api_key
    )
    vector = embeddings.embed_query("test")
    print(f"Dimension: {len(vector)}")

if __name__ == "__main__":
    check_dimension()
