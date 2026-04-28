# import os
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.prompts import PromptTemplate
# from huggingface_hub import AsyncInferenceClient
# from app.database.supabase import supabase_client
# import logging

# logger = logging.getLogger(__name__)

# # 1. Embeddings Initialize (Local/Free)
# embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# # app/agents/multi_agent.py (Line 13 ke aas-paas)

# # app/agents/multi_agent.py (Line 13 ke aas-paas)

# hf_client = AsyncInferenceClient(
#     model="HuggingFaceH4/zephyr-7b-beta", # Changed from Mistral to Zephyr for Chat Compatibility
#     token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
# )

# # 3. Retriever Agent
# async def retriever_agent(user_id: str, question: str):
#     """Fetches relevant context from Supabase pgvector."""
#     query_vector = embeddings_model.embed_query(question)
    
#     response = supabase_client.rpc(
#         "match_documents",
#         {
#             "query_embedding": query_vector,
#             "match_threshold": 0.2, # Threshold thoda kam kiya taaki search aasan ho
#             "match_count": 3,
#             "p_user_id": user_id
#         }
#     ).execute()
    
#     contexts = response.data
    
#     if not contexts:
#         return None
        
#     combined_context = "\n\n".join([doc['content'] for doc in contexts])
#     return combined_context

# # 4 app/agents/multi_agent.py mein sirf is function ko replace karein:

# async def answer_agent(context: str, question: str):
#     """Generates an answer using Hugging Face Chat Completion API."""
#     if not context:
#         return "Fallback Response: I'm sorry, but I couldn't find any relevant information in your uploaded documents to answer this question."

#     # Raw string prompt ki jagah ab hum structured messages list use karenge
#     messages = [
#         {
#             "role": "system",
#             "content": "You are an intelligent AI assistant. Use ONLY the provided context to answer the user's question. If the context does not contain enough information to answer the question, clearly state: 'Fallback Response: Insufficient data.'"
#         },
#         {
#             "role": "user",
#             "content": f"Context:\n{context}\n\nQuestion: {question}"
#         }
#     ]
    
#     try:
#         # text_generation ki jagah chat_completion function call karenge
#         response = await hf_client.chat_completion(
#             messages=messages,
#             max_tokens=512,
#             temperature=0.3
#         )
        
#         # Chat completion object se content extract karna
#         return response.choices[0].message.content.strip()
        
#     except Exception as e:
#         logger.error(f"LLM API Error: {str(e)}")
#         return f"Fallback Response: AI Model error - {str(e)}"

# # 5. Main Agent Coordinator
# async def process_user_query(user_id: str, question: str):
#     try:
#         # Step A: Retrieve context
#         context = await retriever_agent(user_id, question)
        
#         # Step B: Generate Answer
#         final_answer = await answer_agent(context, question)
        
#         return {
#             "question": question,
#             "answer": final_answer,
#             "context_used": context if context else "None"
#         }
#     except Exception as e:
#         logger.error(f"Error in multi-agent pipeline: {str(e)}")
#         raise Exception(f"Agent processing failed: {str(e)}")


import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.database.supabase import supabase_client
import logging

logger = logging.getLogger(__name__)

# 1. Embeddings Initialize (Local/Free) - Yeh same rahega
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Answer Agent ke liye Groq LLM Initialize karna
llm = ChatGroq(
    temperature=0.3, 
    model_name="llama-3.1-8b-instant", # Purane model ki jagah yeh naya aur supported model use karein
    api_key=os.getenv("GROQ_API_KEY")
)

# 3. Retriever Agent (Bilkuk same rahega, isme koi change nahi)
async def retriever_agent(user_id: str, question: str):
    query_vector = embeddings_model.embed_query(question)
    
    response = supabase_client.rpc(
        "match_documents",
        {
            "query_embedding": query_vector,
            "match_threshold": 0.2, 
            "match_count": 3,
            "p_user_id": user_id
        }
    ).execute()
    
    contexts = response.data
    
    if not contexts:
        return None
        
    combined_context = "\n\n".join([doc['content'] for doc in contexts])
    return combined_context

# 4. Updated Answer Agent (Groq ke sath)
async def answer_agent(context: str, question: str):
    """Generates an answer using Groq and Llama-3."""
    if not context:
        return "Fallback Response: I'm sorry, but I couldn't find any relevant information in your uploaded documents to answer this question."

    # LangChain ke proper message formats use kar rahe hain
    messages = [
        SystemMessage(content="You are an intelligent AI assistant. Use ONLY the provided context to answer the user's question. If the context does not contain enough information to answer the question, clearly state: 'Fallback Response: Insufficient data.'"),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
    ]
    
    try:
        # Groq API ko asynchronous call karna
        response = await llm.ainvoke(messages)
        return response.content.strip()
        
    except Exception as e:
        logger.error(f"LLM API Error: {str(e)}")
        return f"Fallback Response: AI Model error - {str(e)}"

# 5. Main Agent Coordinator (Bilkuk same rahega)
async def process_user_query(user_id: str, question: str):
    try:
        context = await retriever_agent(user_id, question)
        final_answer = await answer_agent(context, question)
        
        return {
            "question": question,
            "answer": final_answer,
            "context_used": context if context else "None"
        }
    except Exception as e:
        logger.error(f"Error in multi-agent pipeline: {str(e)}")
        raise Exception(f"Agent processing failed: {str(e)}")