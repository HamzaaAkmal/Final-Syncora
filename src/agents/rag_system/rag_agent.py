"""
RAG Agent
=========

Integrates with orchestrator for PDF-based Q&A.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from src.agents.rag_system.pdf_loader import PDFLoader
from src.agents.rag_system.rag_engine import RAGEngine


class RAGAgent:
    """Agent for PDF-based retrieval and Q&A with local models."""
    
    def __init__(self, project_root: Path = None, model_dir: Path = None):
        """
        Initialize RAG agent with local models.
        
        Args:
            project_root: Project root directory
            model_dir: Directory with local models (defaults to rag_system/models)
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        
        # Use local models folder
        if model_dir is None:
            model_dir = Path(__file__).parent / "models"
        
        # Initialize components with local models
        self.pdf_loader = PDFLoader()
        self.rag_engine = RAGEngine(
            db_path=str(self.project_root / "data" / "vector_db"),
            model_dir=str(model_dir)
        )
        
        # Uploaded PDFs tracking
        self.uploaded_pdfs = {}
    
    def upload_pdf(self, pdf_path: str, collection_name: str = None) -> Dict[str, Any]:
        """
        Upload and index PDF.
        
        Args:
            pdf_path: Path to PDF file
            collection_name: Collection name (defaults to PDF name)
            
        Returns:
            Upload status
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"success": False, "error": f"PDF not found: {pdf_path}"}
            
            # Default collection name
            collection_name = collection_name or pdf_path.stem
            
            # Process PDF
            chunks = self.pdf_loader.process_pdf(str(pdf_path), collection_name)
            
            # Index in RAG engine
            self.rag_engine.index_documents(collection_name, chunks)
            
            # Track upload
            self.uploaded_pdfs[collection_name] = {
                "path": str(pdf_path),
                "num_chunks": len(chunks),
                "status": "indexed"
            }
            
            return {
                "success": True,
                "collection_name": collection_name,
                "num_chunks": len(chunks),
                "message": f"PDF '{collection_name}' indexed successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def answer_question(self, collection_name: str, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Answer question using RAG.
        
        Args:
            collection_name: PDF collection name
            question: Question
            top_k: Number of documents to retrieve
            
        Returns:
            Answer with sources
        """
        try:
            result = self.rag_engine.query(collection_name, question, top_k)
            return {
                "success": True,
                "answer": result["answer"],
                "question": result["question"],
                "sources_count": result["num_retrieved"],
                "sources": result["sources"]
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_pdfs(self) -> Dict[str, Any]:
        """List uploaded PDFs."""
        return {
            "pdfs": self.uploaded_pdfs,
            "count": len(self.uploaded_pdfs),
            "collections": self.rag_engine.get_collections()
        }
    
    def get_pdf_info(self) -> Dict[str, Any]:
        """Get information about PDFs."""
        return self.pdf_loader.get_pdf_info()
    
    async def process_user_input(self, user_input: str, pdf_collection: Optional[str] = None) -> Dict[str, Any]:
        """
        Async wrapper for integration with orchestrator.
        
        Args:
            user_input: User input
            pdf_collection: PDF collection to search
            
        Returns:
            Processing result
        """
        if not pdf_collection:
            return {
                "type": "rag",
                "status": "no_collection",
                "message": "Please specify PDF collection"
            }
        
        result = self.answer_question(pdf_collection, user_input)
        
        return {
            "type": "rag",
            "status": "success" if result["success"] else "error",
            "result": result
        }
