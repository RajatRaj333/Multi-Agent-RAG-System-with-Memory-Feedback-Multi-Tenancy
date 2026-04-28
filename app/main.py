from fastapi import FastAPI
from app.api.routes import router as api_router
from app.database.supabase import supabase_client
from fastapi import APIRouter, HTTPException


app = FastAPI(title="Multi-Agent RAG System API", version="1.0")

# API routes include karna
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "AI Backend System is Running. APIs are ready!"}
  


@app.get("/history/{user_id}")
async def get_conversation_history_api(user_id: str):
    """API endpoint to retrieve past conversations for a user."""
    try:
        response = supabase_client.table("conversations")\
            .select("id, question, answer, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
            
        return {"user_id": user_id, "history": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")