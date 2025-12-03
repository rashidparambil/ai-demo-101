from langchain_google_genai import ChatGoogleGenerativeAI
from api.config import config
from langchain_core.prompts import ChatPromptTemplate
from api.chat_bot.table_detail_repository import TableDetailsRepository
from api.repository.database import SessionLocal

class SQLGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            max_retries=1,
            google_api_key=config.google_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert SQL generator. Given the following database schema and a user query, generate a valid SQL query to answer the user's question.
        
        Schema:
        {schema}
        
        User Query: {query}
        
        Rules:
        1. Generate ONLY the SQL query. Do not include markdown formatting (```sql ... ```) or explanations.
        2. Use standard SQL compatible with PostgreSQL.
        3. If the query cannot be answered with the given schema, return "ERROR: Cannot answer query with available schema."
        4. Do not use destructive commands (DELETE, DROP, UPDATE, INSERT). Only SELECT.
        
        SQL Query:
        """)

    async def generate_sql(self, query: str) -> str:
        """
        Generate SQL query from natural language query using RAG for schema.
        
        Args:
            query: User's natural language query.
            
        Returns:
            Generated SQL query.
        """
        # Retrieve relevant table details
        db = SessionLocal()
        try:
            repo = TableDetailsRepository(db)
            # Search for relevant tables
            table_details = repo.search(query, limit=5)
            
            if not table_details:
                return "ERROR: No relevant tables found for the query."
                
            # Construct schema string from descriptions
            schema = "\n\n".join([td.table_description for td in table_details])
            
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"schema": schema, "query": query})
            return response.content.strip().replace("```sql", "").replace("```", "").strip()
        finally:
            db.close()
