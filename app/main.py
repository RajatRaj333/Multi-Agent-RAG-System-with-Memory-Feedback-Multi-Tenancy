from fastapi import FastAPI
from app.api.routes import router as api_router
from app.database.supabase import supabase_client
from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field
from fastapi import HTTPException
import logging

app = FastAPI(title="Multi-Agent RAG System API", version="1.0")

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
      
      



logger = logging.getLogger(__name__)

# --- Pydantic Schema for Validation ---
class FeedbackRequest(BaseModel):
    conversation_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5") # [cite: 58]
    comment: str = None # [cite: 59]

# --- POST /feedback Endpoint ---
@app.post("/feedback") # [cite: 32]
async def submit_feedback(feedback: FeedbackRequest):
    """Stores user feedback for a specific conversation response."""
    try:
        
        response = supabase_client.table("feedback").insert({
            "conversation_id": feedback.conversation_id,
            "rating": feedback.rating,
            "comment": feedback.comment
        }).execute()

        # 2. Advanced Requirement: Low Quality Marking [cite: 90, 92, 93]
        is_low_quality = feedback.rating < 3
        
        if is_low_quality:
            
             
             
            logger.warning(f"Low quality response flagged for conversation {feedback.conversation_id} with rating {feedback.rating}")

        return {
            "status": "success",
            "message": "Feedback submitted successfully.",
            "is_low_quality_marked": is_low_quality
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")