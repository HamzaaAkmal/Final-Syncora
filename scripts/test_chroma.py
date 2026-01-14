import traceback
from pathlib import Path
import sys
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

try:
    import chromadb
    print('chromadb imported')
    client = chromadb.PersistentClient(path=str(project_root / 'data' / 'vector_db_chroma_test'))
    print('client created')
    coll = client.create_collection(name='test_col', get_or_create=True)
    print('collection created')
    # Small dummy embedding
    coll.add(ids=['a'], embeddings=[[0.1]*384], metadatas=[{'k': 'v'}], documents=['hello'])
    print('added doc')
except Exception:
    traceback.print_exc()
    print('error')
