from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.services.rag_pipeline import process_and_store_document
from app.agents.multi_agent import process_user_query
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Schema for /ask request
class AskRequest(BaseModel):
    user_id: str
    question: str




@router.post("/upload")
async def upload_document(
    user_id: str = Form(..., description="Unique ID of the user"),
    file: UploadFile = File(..., description="Text file to upload")
):
    # ... (Aapka purana upload code yahan rahega, usme koi change nahi hai) ...
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Currently only .txt files are supported.")
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        result = await process_and_store_document(user_id=user_id, text=text_content)
        return {"message": "Document uploaded and processed successfully", "user_id": user_id, "filename": file.filename, "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# NAYA ENDPOINT: Ask Question
@router.post("/ask")
async def ask_question(request: AskRequest):
    """
    Ask a question based on uploaded documents.
    Uses Retriever Agent and Answer Agent (Gemma 3).
    """
    try:
        response = await process_user_query(user_id=request.user_id, question=request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      


