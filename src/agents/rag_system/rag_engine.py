"""
RAG Engine
==========

Retrieval-Augmented Generation using local models.
Uses FLAN-T5 for Q&A generation.
"""

from typing import List, Dict, Any
from pathlib import Path
from transformers import pipeline
from src.agents.rag_system.embedding_service import EmbeddingService
from src.agents.rag_system.vector_db import VectorDBService


class RAGEngine:
    """RAG system with local models (offline)."""
    
    def __init__(self, db_path: str = "data/vector_db", model_dir: str = None):
        """
        Initialize RAG engine with local models.
        
        Args:
            db_path: Vector database path
            model_dir: Directory containing local models (defaults to rag_system/models)
        """
        if model_dir is None:
            model_dir = Path(__file__).parent / "models"
        
        # Initialize services with local models
        embedding_model_path = Path(model_dir) / "all-MiniLM-L6-v2"
        self.embedding_service = EmbeddingService(str(embedding_model_path))
        self.vector_db = VectorDBService(db_path)
        
        # Initialize FLAN-T5 for Q&A (local model, runs offline)
        flan_model_path = Path(model_dir) / "flan-t5-small"
        self.qa_model = pipeline(
            "text2text-generation",
            model=str(flan_model_path),
            device=-1  # CPU (use 0 for GPU if available)
        )
    
    def index_documents(self, collection_name: str, documents: List[Dict[str, Any]]):
        """
        Index documents with embeddings.
        
        Args:
            collection_name: Name of collection
            documents: List of documents with 'content' and 'metadata'
        """
        # Create collection
        self.vector_db.create_collection(collection_name)
        
        # Add embeddings to documents
        for i, doc in enumerate(documents):
            embedding = self.embedding_service.embed_text(doc['content'])
            doc['embeddings'] = embedding
            doc['id'] = i
        
        # Add to vector DB
        try:
            self.vector_db.add_documents(collection_name, documents)
        except Exception as e:
            # Bubble up with clearer message
            raise RuntimeError(f"Vector DB error: {e}")
    
    def retrieve(self, collection_name: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents.
        
        Args:
            collection_name: Collection name
            query: Query text
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        print(f"[RAG_ENGINE] Generating query embedding for: '{query[:50]}...'")
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        print(f"[RAG_ENGINE] Query embedding generated, dimension: {len(query_embedding)}")
        
        # Search vector DB
        print(f"[RAG_ENGINE] Searching vector DB for collection: '{collection_name}'")
        results = self.vector_db.search(collection_name, query_embedding, top_k)
        print(f"[RAG_ENGINE] Vector DB search complete, got {len(results)} results")
        
        return results
    
    def generate_answer(self, context: str, question: str) -> str:
        """
        Generate answer using FLAN-T5, executed in a subprocess to isolate crashes.
        Falls back to returning the context snippet if the worker fails.
        """
        # Create prompt
        prompt = f"""
Context: {context}

Question: {question}

Answer:"""

        # Prepare payload
        import json, tempfile, subprocess, sys, os
        project_root = Path(__file__).resolve().parents[3]
        worker = project_root / 'scripts' / 'flan_worker.py'

        payload = {
            'prompt': prompt,
            'max_new_tokens': 256
        }

        try:
            print(f"[RAG_ENGINE] Starting FLAN worker for question: {question[:50]}...")
            
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tf:
                json.dump(payload, tf)
                tf.flush()
                payload_path = tf.name

            print(f"[RAG_ENGINE] Payload written to: {payload_path}")
            cmd = [sys.executable, str(worker), payload_path]
            print(f"[RAG_ENGINE] Running command: {' '.join(cmd)}")
            
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Clean up temp file
            try:
                os.unlink(payload_path)
            except:
                pass
            
            print(f"[RAG_ENGINE] FLAN worker return code: {proc.returncode}")
            
            if proc.returncode != 0:
                err = proc.stderr or proc.stdout
                print(f"[RAG_ENGINE] FLAN worker error: {err}")
                raise RuntimeError(f"FLAN worker failed: {proc.returncode} - {err}")

            print(f"[RAG_ENGINE] FLAN worker stdout: {proc.stdout[:200]}...")
            result = json.loads(proc.stdout.strip())
            
            if 'generated_text' in result:
                answer = result['generated_text'].strip()
                print(f"[RAG_ENGINE] Generated answer: {answer[:100]}...")
                return answer
            else:
                print(f"[RAG_ENGINE] Invalid response format: {result}")
                raise RuntimeError(f"FLAN worker returned invalid response: {result}")

        except subprocess.TimeoutExpired as e:
            print(f"[RAG_ENGINE] FLAN worker timeout after 60s")
            # Fallback to context
            fallback = context[:400].strip()
            return f"Based on the document: {fallback}... (Answer generation timed out)"
        except Exception as e:
            # Log and fallback to basic answer using context
            print(f"[RAG_ENGINE] Error generating answer: {type(e).__name__}: {e}")
            try:
                # Simple heuristic: return first 400 chars of context with a note
                fallback = context[:400].strip()
                return f"Based on the document: {fallback}..."
            except Exception:
                return "Unable to generate answer at this time. Please try again."
    
    def query(self, collection_name: str, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve + generate.
        
        Args:
            collection_name: Collection name
            question: Question
            top_k: Number of documents to retrieve
            
        Returns:
            Answer with sources
        """
        print(f"[RAG_ENGINE] Starting query: collection='{collection_name}', question='{question[:50]}...', top_k={top_k}")
        
        # Retrieve relevant documents
        print(f"[RAG_ENGINE] Retrieving documents...")
        retrieved_docs = self.retrieve(collection_name, question, top_k)
        
        print(f"[RAG_ENGINE] Retrieved {len(retrieved_docs)} documents")
        
        if not retrieved_docs:
            print(f"[RAG_ENGINE] No documents found for query")
            return {
                "answer": "No relevant documents found.",
                "sources": [],
                "question": question,
                "num_retrieved": 0
            }
        
        # Combine context
        context = "\n".join([doc['content'] for doc in retrieved_docs])
        print(f"[RAG_ENGINE] Combined context length: {len(context)} chars")
        
        # Generate answer
        print(f"[RAG_ENGINE] Generating answer...")
        answer = self.generate_answer(context, question)
        print(f"[RAG_ENGINE] Answer generated successfully")
        
        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc['content'][:200],  # First 200 chars
                    "metadata": doc['metadata']
                }
                for doc in retrieved_docs
            ],
            "question": question,
            "num_retrieved": len(retrieved_docs)
        }
    
    def get_collections(self) -> List[str]:
        """Get all collections."""
        return self.vector_db.list_collections()
