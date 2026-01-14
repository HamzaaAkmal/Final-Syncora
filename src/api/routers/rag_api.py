"""
RAG API Router
==============

REST endpoints for PDF upload and Q&A using RAG.
"""

import uuid
from pathlib import Path
import sys

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from src.agents.rag_system import RAGAgent
from src.logging import get_logger
from src.api.utils.history import ActivityType, history_manager

# Initialize
project_root = Path(__file__).parent.parent.parent.parent
logger = get_logger("RAG_API", level="INFO")
router = APIRouter()

# Initialize RAG agent
try:
    rag_agent = RAGAgent(project_root=project_root)
except Exception as e:
    logger.warning(f"RAG agent initialization failed: {e}")
    rag_agent = None


# =============================================================================
# Pydantic Models
# =============================================================================

class RAGQueryRequest(BaseModel):
    """RAG query request."""
    question: str
    collection_name: str
    top_k: int = 3


class RAGUploadResponse(BaseModel):
    """RAG upload response."""
    success: bool
    collection_name: Optional[str] = None
    num_chunks: Optional[int] = None
    message: str


# =============================================================================
# Background task for processing
# =============================================================================

def process_pdf_task(file_path: str, collection_name: str):
    """Background task to process PDF"""
    try:
        logger.info(f"[RAG] Background processing started for: {file_path}")
        result = rag_agent.upload_pdf(file_path, collection_name)
        logger.info(f"[RAG] Background processing complete: {result}")
        return result
    except Exception as e:
        logger.error(f"[RAG] Background processing failed: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


# =============================================================================
# RAG Endpoints
# =============================================================================

@router.post("/rag/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_name: Optional[str] = Form(None)
):
    """
    Upload PDF for RAG indexing.
    
    Args:
        background_tasks: FastAPI background tasks
        file: PDF file
        collection_name: Collection name (optional, defaults to filename)
    """
    logger.info(f"[RAG] Upload request received: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
    
    if rag_agent is None:
        logger.error("[RAG] RAG system not available")
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        if not file.filename.endswith('.pdf'):
            logger.warning(f"[RAG] Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files allowed")
        
        # Save uploaded file
        upload_dir = project_root / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
        
        logger.info(f"[RAG] Saving file to: {file_path}")
        
        # Write file
        try:
            contents = await file.read()
            logger.info(f"[RAG] File read successfully, size: {len(contents)} bytes")
            
            with open(file_path, 'wb') as f:
                f.write(contents)
            
            logger.info(f"[RAG] File saved successfully")
        except Exception as e:
            logger.error(f"[RAG] Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Use filename as default collection name
        final_collection_name = collection_name or Path(file.filename).stem

        # Sanitize collection name for backend storage (Chroma requires restricted names)
        try:
            from src.agents.rag_system.vector_db import sanitize_collection_name
            sanitized_name = sanitize_collection_name(final_collection_name)
            if sanitized_name != final_collection_name:
                logger.info(f"[RAG] Collection name sanitized: '{final_collection_name}' -> '{sanitized_name}'")
            final_collection_name = sanitized_name
        except Exception:
            # If sanitizer is unavailable, proceed with original name (it will fail later if invalid)
            logger.warning("[RAG] Collection name sanitizer unavailable")

        # Add background task for processing
        background_tasks.add_task(process_pdf_task, str(file_path), final_collection_name)
        
        logger.info(f"[RAG] PDF saved, processing queued for background")
        
        # Return immediately with success (collection name is sanitized)
        return {
            "success": True,
            "collection_name": final_collection_name,
            "message": f"PDF '{file.filename}' uploaded. Processing in background...",
            "status": "processing"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[RAG] Unexpected error uploading PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/query")
async def query_rag(request: RAGQueryRequest):
    """
    Query RAG system.
    
    Args:
        request: Query request with question, collection_name, top_k
    """
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        result = rag_agent.answer_question(
            request.collection_name,
            request.question,
            request.top_k
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"RAG query processed: {request.question[:50]}...")
        
        # Save to history
        try:
            answer_summary = result.get("answer", "")[:100] if result.get("answer") else "No answer"
            history_manager.add_entry(
                activity_type=ActivityType.RAG,
                title=f"{request.collection_name} - Q&A",
                content={
                    "question": request.question,
                    "answer": result.get("answer", ""),
                    "collection_name": request.collection_name,
                    "sources_count": result.get("sources_count", 0),
                    "sources": result.get("sources", [])
                },
                summary=answer_summary
            )
        except Exception as hist_err:
            logger.warning(f"Failed to save RAG history: {hist_err}")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/collections")
async def list_collections():
    """List all uploaded PDF collections."""
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        pdfs_info = rag_agent.list_pdfs()
        return pdfs_info
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """Get information about specific collection."""
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        pdfs = rag_agent.list_pdfs()
        
        if collection_name not in pdfs["pdfs"]:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return {
            "collection_name": collection_name,
            "info": pdfs["pdfs"][collection_name]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rag/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection (not fully implemented - collections auto-persist)."""
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        if collection_name in rag_agent.uploaded_pdfs:
            del rag_agent.uploaded_pdfs[collection_name]
            return {"success": True, "message": f"Collection {collection_name} removed from tracking"}
        else:
            raise HTTPException(status_code=404, detail="Collection not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/health")
async def rag_health():
    """RAG system health check."""
    if rag_agent is None:
        return {"status": "unavailable", "reason": "RAG system not initialized"}
    
    try:
        collections = rag_agent.rag_engine.get_collections()
        return {
            "status": "healthy",
            "collections": len(collections),
            "models": {
                "embeddings": "all-MiniLM-L6-v2",
                "qa": "google/flan-t5-small"
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
