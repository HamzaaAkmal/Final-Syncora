import sys
import time
import traceback
import logging
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.basicConfig(level=logging.INFO)

project_root = Path(__file__).resolve().parents[1]
fp = project_root / 'data' / 'uploads' / '72c9ecca-bc56-466d-bb4c-1436750095f4_LimitX_Pitch_Deck_Analysis.pdf'
from src.agents.rag_system import RAGAgent

agent = RAGAgent(project_root=Path('.'))
print('Starting upload_pdf for', fp)

t0 = time.time()
try:
    res = agent.upload_pdf(str(fp))
    print('Result:', res)
    print('>>> UPLOAD_FINISHED')
except Exception:
    traceback.print_exc()
    print('Exception during upload')
finally:
    print('Elapsed', time.time() - t0)
    sys.stdout.flush()
