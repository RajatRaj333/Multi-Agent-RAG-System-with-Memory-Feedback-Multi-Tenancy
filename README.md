# Multi-Agent RAG Backend System

A production-grade, multi-tenant AI backend system designed to process user documents, retrieve context using vector similarity search, and generate accurate answers using a Multi-Agent architecture. The system features conversational memory, a user feedback loop, and strict data isolation per user.

##  Core Features

* **Multi-Tenant Architecture:** Strict data isolation ensuring users can only query and access their own documents and conversation history.
* **Multi-Agent RAG Pipeline:**
  * **Retriever Agent:** Performs FAISS-style similarity search using `pgvector` to fetch the top-k relevant document chunks.
  * **Answer Agent:** Analyzes the retrieved context and conversation history to generate an accurate response or triggers a fallback if data is insufficient.
* **Conversational Memory:** Maintains the last 'N' interactions per user to handle follow-up questions contextually.
* **Automated Feedback Loop:** Users can rate responses (1-5). Responses with a rating < 3 are automatically flagged as low-quality.

##  Technology Stack

* **Backend Framework:** FastAPI (Python) 
* **Database & Vector Store:** Supabase (PostgreSQL) with the `pgvector` extension.
* **Embeddings Model:** `all-MiniLM-L6-v2` (via HuggingFace) for fast, 384-dimensional local vector generation.
* **LLM (Text Generation):** `llama-3.1-8b-instant` (via Groq API) for high-speed, accurate reasoning.
* **Orchestration:** LangChain for document chunking (RecursiveCharacterTextSplitter) and prompt management.

##  Database Schema (Supabase)

The system utilizes a relational structure with the following key tables:
1. `users`: Stores unique user identifiers.
2. `documents`: Stores document text chunks and their 384-dimensional `vector` embeddings.
3. `conversations`: Stores the user query, AI answer, and the JSON context used (Context Memory).
4. `feedback`: Links to conversations to store user ratings and comments.

##  Setup & Installation

### 1. Prerequisites
* Python 3.10+
* A Supabase project with the `pgvector` extension enabled.
* A Groq API Key.

### 2. Clone the Repository
```bash
# git clone <your-repository-url>
# cd ai_backend_assignment


# 2.. Create a virtual environment and install dependencies:

# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate
# pip install -r requirements.txt


# 3. Environment Variables:
# Create a .env file in the root directory and add your keys:

# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_anon_key
# GROQ_API_KEY=your_groq_api_key


# 4 Run the server:

# uvicorn app.main:app --reload