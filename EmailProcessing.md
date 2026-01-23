## Email Processing Overview

### **Purpose**
Automates extraction and validation of financial data from emails using AI and business rules.

---

### **Key Packages & Frameworks Used**

- **[FastAPI](https://fastapi.tiangolo.com/):**  
  For building the API endpoints and serving the application.

- **[LangChain](https://python.langchain.com/):**  
  Used for orchestrating the AI agent, tool integration, and workflow management.

- **[langchain-google-genai](https://python.langchain.com/docs/integrations/llms/google_genai):**  
  Integrates Google Gemini (Generative AI) models as the LLM backend for extraction and validation.

- **[langchain-mcp-adapters](https://pypi.org/project/langchain-mcp-adapters/):**  
  For connecting to the MCP (rules engine) and loading custom tools for validation and transformation.

---

### **How It Works**

#### **Initialization**
- Loads configuration (API keys, MCP server URL).
- Prepares a detailed workflow for the AI agent to follow.

#### **Processing a Message**
- Creates a new session with the MCP (rules engine) for each request.
- Loads custom tools and MCP tools for validation and transformation.
- Sets up a Google Gemini LLM agent with strict instructions.
- Generates a unique correlation ID for tracking.

#### **Workflow Steps**
1. **Subject Validation:**  
   Checks if the email subject is valid.
2. **Client Verification:**  
   Confirms the client exists.
3. **Rule Retrieval:**  
   Gets all validation/transformation rules for the client and process type.
4. **Data Extraction & Validation:**  
   - Extracts records from the email.
   - Applies transformation rules (e.g., formatting) first, then validation rules (e.g., required fields).
   - Documents every rule applied, including status and details.
5. **Finalization:**  
   - Calls tools to check account rules, save results, and log the process.
   - Returns a comprehensive JSON with all results, errors, and applied rules.

---

### **Key Features**
- **Strict, step-by-step validation:** Stops and returns error if any critical step fails.
- **Full traceability:** All actions and rule applications are fully documented in the output.
- **Auditability:** Designed for easy review and compliance.