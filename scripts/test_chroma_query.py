"""
Test ChromaDB Query
===================

Isolate and test ChromaDB query operations to find where it hangs.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import chromadb
import time

def test_chroma_query():
    """Test ChromaDB query operation step by step."""
    
    print("=" * 60)
    print("ChromaDB Query Test")
    print("=" * 60)
    
    # Setup paths
    db_path = project_root / "data" / "vector_db"
    print(f"\n[1] DB Path: {db_path}")
    print(f"    Exists: {db_path.exists()}")
    
    # Initialize client
    print("\n[2] Initializing ChromaDB client...")
    start = time.time()
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        print(f"    ✓ Client initialized in {time.time() - start:.2f}s")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return
    
    # List collections
    print("\n[3] Listing collections...")
    start = time.time()
    try:
        collections = client.list_collections()
        print(f"    ✓ Found {len(collections)} collections in {time.time() - start:.2f}s")
        
        print(f"\n[3.1] Iterating collections...")
        for i, coll in enumerate(collections):
            print(f"      [{i}] Name: {coll.name}")
            
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not collections:
        print("\n⚠ No collections found. Upload a PDF first.")
        return
    
    # Pick first collection
    collection_name = collections[0].name
    print(f"\n[4] Testing with collection: {collection_name}")
    
    # Get collection
    print(f"\n[5] Getting collection '{collection_name}'...")
    start = time.time()
    try:
        collection = client.get_collection(name=collection_name)
        print(f"    ✓ Collection retrieved in {time.time() - start:.2f}s")
        # Skip count as it seems to crash
        # print(f"    Count: {collection.count()}")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create a dummy query embedding
    print(f"\n[6] Creating dummy query embedding...")
    start = time.time()
    try:
        from sentence_transformers import SentenceTransformer
        model_path = project_root / "src" / "agents" / "rag_system" / "models" / "all-MiniLM-L6-v2"
        print(f"    Model path: {model_path}")
        print(f"    Exists: {model_path.exists()}")
        
        model = SentenceTransformer(str(model_path))
        print(f"    ✓ Model loaded in {time.time() - start:.2f}s")
        
        query_text = "what is this about?"
        query_embedding = model.encode(query_text).tolist()
        print(f"    ✓ Embedding generated, dimension: {len(query_embedding)}")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return
    
    # Query the collection
    print(f"\n[7] Querying collection (top_k=3)...")
    print(f"    Query: '{query_text}'")
    print(f"    Embedding dimension: {len(query_embedding)}")
    print(f"    Starting query with 10s timeout...")
    
    start = time.time()
    try:
        # Set a timeout using threading
        import threading
        
        result_container = {}
        exception_container = {}
        
        def query_with_timeout():
            try:
                print(f"    [Thread] Starting ChromaDB query...")
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3
                )
                print(f"    [Thread] Query completed!")
                result_container['results'] = results
            except Exception as e:
                print(f"    [Thread] Exception: {e}")
                exception_container['error'] = e
        
        thread = threading.Thread(target=query_with_timeout)
        thread.daemon = True
        thread.start()
        print(f"    Query thread started, waiting...")
        
        # Wait with timeout
        timeout = 10  # 10 seconds
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            print(f"    ✗ TIMEOUT after {timeout}s - Query is hanging!")
            print(f"    This indicates ChromaDB query is blocking indefinitely.")
            print(f"\n⚠ DIAGNOSIS: ChromaDB query operation is hanging.")
            print(f"   Possible causes:")
            print(f"   1. ChromaDB database corruption")
            print(f"   2. Index not properly built")
            print(f"   3. Threading/locking issue in ChromaDB")
            return
        
        if 'error' in exception_container:
            raise exception_container['error']
        
        results = result_container.get('results')
        elapsed = time.time() - start
        
        print(f"    ✓ Query completed in {elapsed:.2f}s")
        print(f"\n[8] Results:")
        
        if results and results['documents'] and results['documents'][0]:
            num_results = len(results['documents'][0])
            print(f"    Found {num_results} results")
            
            for i, doc in enumerate(results['documents'][0]):
                print(f"\n    Result {i+1}:")
                print(f"      Content (first 100 chars): {doc[:100]}...")
                if results['metadatas'] and results['metadatas'][0]:
                    print(f"      Metadata: {results['metadatas'][0][i]}")
                if results['distances'] and results['distances'][0]:
                    print(f"      Distance: {results['distances'][0][i]:.4f}")
        else:
            print(f"    No results returned")
        
        print(f"\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"    ✗ Query failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    test_chroma_query()
