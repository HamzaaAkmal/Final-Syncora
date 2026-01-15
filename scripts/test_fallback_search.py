"""Simple test to verify fallback search works"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.rag_system.vector_db import VectorDBService
from src.agents.rag_system.embedding_service import EmbeddingService

print("Testing VectorDB Fallback Search")
print("="*60)

# Initialize services
db_path = project_root / "data" / "vector_db"
print(f"DB Path: {db_path}")

vector_db = VectorDBService(str(db_path))
print("VectorDB initialized")

embedding_service = EmbeddingService()
print("Embedding service initialized")

# Test query
collection_name = "AgentX-AI-Hackathon-Challenges"
query = "what is agentx?"

print(f"\nTesting search:")
print(f"  Collection: {collection_name}")
print(f"  Query: {query}")

# Generate embedding
query_embedding = embedding_service.embed_text(query)
print(f"  Embedding generated: {len(query_embedding)} dimensions")

# Search
results = vector_db.search(collection_name, query_embedding, top_k=3)
print(f"\nResults: {len(results)} found")

for i, result in enumerate(results):
    print(f"\n[{i+1}] Distance: {result.get('distance', 'N/A'):.4f}")
    print(f"    Content (first 150 chars): {result['content'][:150]}...")
    print(f"    Metadata: {result.get('metadata', {})}")

print("\nTest completed!")
