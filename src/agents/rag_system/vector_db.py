"""
Vector Database Service
=======================

Local vector database using Chroma (offline).
"""

import chromadb
from pathlib import Path
from typing import List, Dict, Any


import re
import hashlib


def sanitize_collection_name(name: str) -> str:
    """Sanitize a collection name to match Chroma's constraints:
    - Allowed characters: a-zA-Z0-9._-
    - Must start and end with an alphanumeric character
    - Length between 3 and 512
    Replaces disallowed characters with '-', trims leading/trailing non-alnum,
    and appends a short hash suffix if necessary for uniqueness.
    """
    if not isinstance(name, str):
        name = str(name)

    # Replace disallowed characters with '-'
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", name)

    # Trim leading/trailing separators or non-alnum
    sanitized = re.sub(r"^[^A-Za-z0-9]+", "", sanitized)
    sanitized = re.sub(r"[^A-Za-z0-9]+$", "", sanitized)

    # Enforce length limits
    if len(sanitized) < 3:
        # Append a hash to make it unique enough
        h = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
        sanitized = (sanitized + "-" + h)[:6]
    if len(sanitized) > 512:
        sanitized = sanitized[:512]

    # Final safety: ensure it starts/ends with alnum
    sanitized = re.sub(r"^[^A-Za-z0-9]+", "", sanitized)
    sanitized = re.sub(r"[^A-Za-z0-9]+$", "", sanitized)

    if sanitized == "":
        sanitized = "collection-" + hashlib.md5(name.encode("utf-8")).hexdigest()[:6]

    return sanitized


class VectorDBService:
    """Manage vector database with Chroma."""
    
    def __init__(self, db_path: str = "data/vector_db"):
        """
        Initialize vector database.
        
        Args:
            db_path: Path to store database
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collections = {}
    
    def create_collection(self, collection_name: str, metadata: Dict[str, Any] = None):
        """
        Create new collection.
        
        Args:
            collection_name: Name of collection
            metadata: Collection metadata
        """
        sanitized = sanitize_collection_name(collection_name)
        if sanitized != collection_name:
            # Log sanitization for debugging (avoid circular import of logger here)
            print(f"[VectorDB] Collection name sanitized: '{collection_name}' -> '{sanitized}'")

        collection = self.client.create_collection(
            name=sanitized,
            metadata=metadata or {"type": "pdf"},
            get_or_create=True
        )
        self.collections[sanitized] = collection
        return collection
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]):
        """
        Add documents to collection using a subprocess worker to avoid crashing the main process
        if the underlying vector DB has native crashes (observed on some platforms).
        
        This writes the documents to a temporary JSON payload and invokes the worker script
        which performs the Chroma add operation in a separate process.
        """
        payload_dir = self.db_path / "_payloads"
        payload_dir.mkdir(parents=True, exist_ok=True)

        payload = {
            "collection_name": collection_name,
            "documents": [
                {
                    "id": f"{collection_name}_{doc.get('id', i)}",
                    "content": doc['content'],
                    "embeddings": doc['embeddings'],
                    "metadata": (doc.get('metadata') or {"source": collection_name, "doc_index": i})
                }
                for i, doc in enumerate(documents)
            ]
        }

        import json, tempfile, subprocess, sys
        payload_file = payload_dir / f"payload_{collection_name}.json"
        payload_file.write_text(json.dumps(payload))

        worker = Path(__file__).resolve().parents[3] / 'scripts' / 'chroma_worker.py'
        cmd = [sys.executable, str(worker), str(self.db_path), str(payload_file)]

        # Run worker
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                # Log and raise error so caller can handle
                err = proc.stderr or proc.stdout
                raise RuntimeError(f"Chroma worker failed: {proc.returncode} - {err}")
            # Success: register collection locally
            collection = self.create_collection(collection_name)
            return True
        except Exception as e:
            # Fallback: persist documents to JSON so we can search via numpy
            fallback_dir = self.db_path / "fallback"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            fallback_file = fallback_dir / f"{collection_name}.json"
            try:
                import json
                fallback_data = payload
                fallback_file.write_text(json.dumps(fallback_data))
                return True
            except Exception as e2:
                raise RuntimeError(f"Failed to add documents to vector DB and fallback failed: {e}; fallback error: {e2}")
    
    def search(self, collection_name: str, query_embedding: List[float], 
               top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            collection_name: Collection name
            query_embedding: Query embedding vector
            top_k: Number of results
            
        Returns:
            List of similar documents
        """
        # If Chroma collection exists, use it
        if collection_name in self.collections:
            collection = self.collections[collection_name]
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            formatted = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            return formatted

        # Fallback: check for JSON-based storage
        fallback_file = self.db_path / "fallback" / f"{collection_name}.json"
        if fallback_file.exists():
            try:
                import json, numpy as np
                data = json.loads(fallback_file.read_text())
                docs = data.get('documents', [])
                if not docs:
                    return []
                embeddings = np.array([d['embeddings'] for d in docs])
                q = np.array(query_embedding)
                # cosine similarity
                norms = np.linalg.norm(embeddings, axis=1) * (np.linalg.norm(q) + 1e-12)
                sims = (embeddings @ q) / norms
                idxs = sims.argsort()[::-1][:top_k]
                results = []
                for idx in idxs:
                    results.append({
                        'content': docs[int(idx)]['content'],
                        'metadata': docs[int(idx)].get('metadata', {}),
                        'distance': float(1.0 - float(sims[int(idx)]))
                    })
                return results
            except Exception:
                return []

        return []
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        return list(self.collections.keys())
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        if collection_name not in self.collections:
            return {}
        
        collection = self.collections[collection_name]
        return {
            "name": collection_name,
            "count": collection.count()
        }
