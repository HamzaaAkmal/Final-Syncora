"""
RAG System
==========

Offline RAG system using local models:
- Embeddings: all-MiniLM-L6-v2 (local)
- Vector DB: Chroma (local)
- Q&A Model: FLAN-T5 small (local)
- PDFs: User-uploaded files

No LLM API required - everything runs locally and offline.
"""

from src.agents.rag_system.pdf_loader import PDFLoader
from src.agents.rag_system.embedding_service import EmbeddingService
from src.agents.rag_system.vector_db import VectorDBService
from src.agents.rag_system.rag_engine import RAGEngine
from src.agents.rag_system.rag_agent import RAGAgent

__all__ = [
    "PDFLoader",
    "EmbeddingService",
    "VectorDBService",
    "RAGEngine",
    "RAGAgent"
]
