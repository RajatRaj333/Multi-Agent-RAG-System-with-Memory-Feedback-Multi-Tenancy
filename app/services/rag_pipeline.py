from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from app.database.supabase import supabase_client
import logging

# Logger setup for debugging
logger = logging.getLogger(__name__)

# OpenAI ki jagah Free HuggingFace Embedding Model initialize karna (Runs locally)
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def process_and_store_document(user_id: str, text: str):
    try:
        # 1. Document Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # 2. Embeddings Generate karna aur Database mein store karna
        records_to_insert = []
        for chunk in chunks:
            # Har chunk ka vector generate karna (Ab yeh free/local chalega)
            vector = embeddings_model.embed_query(chunk)
            
            # Database record prepare karna
            records_to_insert.append({
                "user_id": user_id,
                "content": chunk,
                "embedding": vector
            })
            
        # 3. Supabase pgvector mein bulk insert karna
        response = supabase_client.table("documents").insert(records_to_insert).execute()
        
        return {"status": "success", "chunks_stored": len(chunks)}
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise Exception(f"Failed to process and store document: {str(e)}")