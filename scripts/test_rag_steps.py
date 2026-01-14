import sys, traceback, time, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

fp = project_root / 'data' / 'uploads' / '72c9ecca-bc56-466d-bb4c-1436750095f4_LimitX_Pitch_Deck_Analysis.pdf'
print('File:', fp)

try:
    from src.agents.rag_system.pdf_loader import PDFLoader
    from src.agents.rag_system.embedding_service import EmbeddingService
    from src.agents.rag_system.vector_db import VectorDBService

    loader = PDFLoader()
    print('Extracting text...')
    t0 = time.time()
    text = loader.extract_text_from_pdf(str(fp))
    print('Text length:', len(text))
    print('First 200 chars:', text[:200].replace('\n',' '))
    print('Extract time:', time.time()-t0)

    print('Chunking...')
    chunks = loader.chunk_text(text, metadata={'source': fp.name})
    print('Num chunks:', len(chunks))
    print('Chunk 0 sample:', chunks[0]['content'][:200])

    emb = EmbeddingService()
    sample_texts = [c['content'] for c in chunks[:3]]
    print('Embedding sample texts...')
    t0 = time.time()
    embeddings = emb.embed_texts(sample_texts)
    print('Embeddings count:', len(embeddings), 'dim:', len(embeddings[0]))
    print('Embedding time:', time.time()-t0)

    db = VectorDBService(db_path=str(project_root / 'data' / 'vector_db_test'))
    docs = []
    for i, (txt, emb_) in enumerate(zip(sample_texts, embeddings)):
        docs.append({'id': i, 'content': txt, 'embeddings': emb_, 'metadata': {'source': fp.name}})

    print('Adding to vector DB...')
    try:
        db.add_documents('test_collection', docs)
        print('Added to DB')
    except Exception:
        traceback.print_exc()
        print('Failed to add to DB')

except Exception:
    traceback.print_exc()
    print('Step failed')
