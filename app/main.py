from fastapi import FastAPI
from app.api.routes import router as api_router
from app.database.supabase import supabase_client

app = FastAPI(title="Multi-Agent RAG System API", version="1.0")

# API routes include karna
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "AI Backend System is Running. APIs are ready!"}