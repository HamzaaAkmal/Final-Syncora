import sys, json, traceback
from pathlib import Path

try:
    import chromadb
except Exception as e:
    print('import-error', str(e))
    sys.exit(2)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: chroma_worker.py <db_path> <payload_json>')
        sys.exit(1)
    db_path = sys.argv[1]
    payload_path = sys.argv[2]

    try:
        payload = json.loads(Path(payload_path).read_text())
        collection_name = payload['collection_name']
        docs = payload['documents']

        client = chromadb.PersistentClient(path=db_path)
        collection = client.create_collection(name=collection_name, get_or_create=True)

        ids = [d['id'] for d in docs]
        embeddings = [d['embeddings'] for d in docs]
        metadatas = [d.get('metadata', {}) for d in docs]
        documents = [d['content'] for d in docs]

        collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        print('added')
    except Exception as e:
        traceback.print_exc()
        sys.exit(3)
