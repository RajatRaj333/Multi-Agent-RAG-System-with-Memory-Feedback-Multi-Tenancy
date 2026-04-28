

import json
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
# Updated Answer Agent with Memory
async def answer_agent(context: str, question: str, history: list):
    if not context and not history:
        return "Fallback Response: I'm sorry, but I couldn't find any relevant information."

    # System Message
    messages = [
        SystemMessage(content="You are an intelligent AI assistant. Use the provided context and conversation history to answer the user's question. If you don't know the answer based on these, say 'Fallback Response: Insufficient data.'")
    ]
    
    # Injecting History into the prompt
    for chat in history:
        messages.append(HumanMessage(content=chat['question']))
        messages.append(SystemMessage(content=chat['answer'])) # Treating past answers as system knowledge
        
    # Adding the current query and retrieved context
    current_prompt = f"Context:\n{context}\n\nCurrent Question: {question}"
    messages.append(HumanMessage(content=current_prompt))
    
    try:
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"LLM API Error: {str(e)}")
        return f"Fallback Response: AI Model error - {str(e)}"

# Updated Main Coordinator
async def process_user_query(user_id: str, question: str):
    try:
        # 1. Pichli conversations fetch karein (Memory)
        history = get_recent_history(user_id, limit=3)
        
        # 2. Naya context retrieve karein
        context = await retriever_agent(user_id, question)
        
        # 3. LLM se answer generate karein (History + Context pass karke)
        final_answer = await answer_agent(context, question, history)
        
        # 4. Is nayi conversation ko database mein save karein
        save_conversation(user_id, question, final_answer, context if context else "None")
        
        return {
            "question": question,
            "answer": final_answer,
            "context_used": context if context else "None"
        }
    except Exception as e:
        logger.error(f"Error in multi-agent pipeline: {str(e)}")
        raise Exception(f"Agent processing failed: {str(e)}")
      
import json

# --- Helper Functions for Memory ---

def save_conversation(user_id: str, question: str, answer: str, context_used: str):
    """Saves the current question, answer, and context to the database."""
    try:
        # Context ko JSON strings mein convert kar rahe hain taaki DB mein properly save ho
        context_json = json.dumps({"context": context_used})
        
        supabase_client.table("conversations").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "context_used": context_json
        }).execute()
    except Exception as e:
        logger.error(f"Failed to save conversation: {str(e)}")

def get_recent_history(user_id: str, limit: int = 3):
    """Fetches the last N conversations for a specific user to build memory."""
    try:
        response = supabase_client.table("conversations")\
            .select("question, answer")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        # Puraani chats ko pehle rakhne ke liye list ko reverse kar rahe hain
        history = response.data[::-1]
        return history
    except Exception as e:
        logger.error(f"Failed to fetch history: {str(e)}")
        return []