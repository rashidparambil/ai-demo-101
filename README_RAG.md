# RAG & Text-to-SQL Implementation Demo

This document explains the Retrieval-Augmented Generation (RAG) and Text-to-SQL implementation within the `chat` module (`src/api/chat_bot`). The system enables users to query a database using natural language by dynamically providing relevant database schema context to the LLM.

## Overview

The application uses **Google Gemini** (via LangChain) to convert natural language questions into SQL queries. Instead of feeding the entire database schema to the LLM (which can be too large), we use **RAG** to retrieve only the relevant table descriptions based on the user's query.

### Architecture Flow

1.  **User Query**: User asks a question (e.g., "Show me clients with active rules").
2.  **Schema Retrieval (RAG)**: The system searches for relevant table definitions using vector embeddings.
3.  **Prompt Construction**: The Agent receives the user query + the retrieved schema (Table names, columns, descriptions).
4.  **SQL Generation**: The Agent generates a valid SQL `SELECT` query.
5.  **Execution**: The system executes the SQL against the database.
6.  **Response**: The Agent synthesizes the SQL results into a natural language answer.

---

## 1. Initial Processing & Indexing (Embedding Configuration)

Before the system can answer questions, we must perform an **initial processing** step to "index" our database schema. This involves configuring the `table_details` so the RAG system performs accurate retrieval.

### Why this is needed
The LLM does not inherently know about your specific database structure. We must "teach" it by converting human-readable table descriptions into machine-understandable vectors (embeddings). This is a **one-time setup** (or update-on-change) process.

### Implementation Details (`table_detail_repository.py`)
The `TableDetailsRepository` class initializes the connection to the embedding model:

```python
class TableDetailsRepository:
    def __init__(self, db: Session):
        # Configure the Vector Embedding Model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=config.google_api_key
        )
```

### The Indexing Process
When you call the `add` method (via the `POST /table-details` endpoint), the following processing occurs:

1.  **Receive Input**: The system takes a natural language description of a table.
2.  **Vectorize**: The `self.embeddings.embed_query(table_description)` method contacts Google's API to transform the text into a high-dimensional vector.
3.  **Persist**: This vector is stored in the `embedding` column of the `table_details` table alongside the original text.

```python
def add(self, table_description: str) -> TableDetails:
    # 1. Generate embedding from text
    embedding = self.embeddings.embed_query(table_description)
    
    # 2. Store both text and vector
    db_item = TableDetailsTable(
        table_description=table_description,
        embedding=embedding
    )
    self.db.add(db_item)
    # ...
```

This "indexed" data is what allows the `search` function to later calculate semantic similarity.

---

## 2. RAG Implementation (Schema Retrieval)

The RAG component is responsible for finding the right tables for the job. It does not retrieve the *data* rows for the prompt, but rather the *metadata* (schema) needed to write the query.

### Files Involved
-   `src/api/chat_bot/table_detail_repository.py`: Handles embedding generation and vector search.
-   `src/api/chat_bot/models.py`: Defines the `TableDetails` entity.

---

## 3. Embedding Retrieval

When a user asks a question, we need to find the tables that are semantically related to that question.

### Process
1.  **Input**: User's natural language query.
2.  **Query Embedding**: The query is converted into a vector using the same Gemini model.
3.  **Vector Search**: The system calculates the L2 distance (Euclidean distance) between the query vector and the stored table vectors.
4.  **Selection**: The top 5 most similar table descriptions are returned.

### Code Reference
*From `src/api/chat_bot/table_detail_repository.py`:*
```python
def search(self, query: str, limit: int = 5) -> List[TableDetails]:
    query_embedding = self.embeddings.embed_query(query)
    
    # Order by distance (closest vectors first)
    stmt = select(TableDetailsTable).order_by(
        TableDetailsTable.embedding.l2_distance(query_embedding)
    ).limit(limit)
    
    results = self.db.execute(stmt).scalars().all()
    # ...
```

---

## 4. Result Generation (Text-to-SQL)

Once the relevant schema is retrieved, the **LangChain Agent** takes over.

### Process
1.  **Tool Selection**: The `ChatBotService` initializes an Agent with two tools:
    *   `search_table_details_tool`: To find schema (RAG step).
    *   `execute_sql_tool`: To run the query.
2.  **Reasoning**: The Agent decides to call `search_table_details_tool` first.
3.  **SQL Generation**: Based on the schema returned by the tool, the Agent (driven by the system prompt in `service.py`) generates a valid SQL query.
4.  **Final Answer**: The SQL result is fed back to the LLM to generate the final natural language response.

### Code Reference
*From `src/api/chat_bot/service.py`:*
```python
self.system_message = """You are a helpful data assistant.
    1. Use `search_table_details_tool` to find relevant tables...
    3. **SQL GENERATION:** Generate a valid SQL SELECT query...
    4. **FINAL ANSWER GENERATION:** Return a structured output...
"""
```
