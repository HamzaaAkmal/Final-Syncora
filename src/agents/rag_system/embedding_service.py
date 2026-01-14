"""
Embedding Service
=================

Uses local HuggingFace model for embeddings (offline).
"""

from typing import List
from pathlib import Path
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Generate embeddings using local model."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize embedding service with local model.
        
        Args:
            model_path: Path to local model (defaults to rag_system/models/all-MiniLM-L6-v2)
        """
        if model_path is None:
            # Use local model in rag_system folder
            model_path = Path(__file__).parent / "models" / "all-MiniLM-L6-v2"
        
        self.model_path = str(model_path)
        self.model = SentenceTransformer(self.model_path)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
