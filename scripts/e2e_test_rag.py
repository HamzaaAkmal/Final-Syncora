import time, json, requests, sys
from pathlib import Path

BASE_URL = 'http://localhost:8001'
PDF_PATH = Path('data/uploads/72c9ecca-bc56-466d-bb4c-1436750095f4_LimitX_Pitch_Deck_Analysis.pdf')

print('Uploading PDF...')
files = {'file': open(PDF_PATH, 'rb')}
res = requests.post(BASE_URL + '/api/v1/rag/upload', files=files)
print('Upload HTTP:', res.status_code, res.text[:200])
if res.status_code != 200:
    sys.exit(1)

data = res.json()
collection = data.get('collection_name')
print('Collection:', collection)

print('Polling for collection to be ready...')
# We will try querying until it returns a non-empty answer
for i in range(20):
    time.sleep(1)
    try:
        r = requests.post(BASE_URL + '/api/v1/rag/query', json={'question':'What is the overall rating?','collection_name':collection,'top_k':3}, timeout=10)
        print('Query attempt', i, 'status', r.status_code)
        if r.status_code == 200:
            print('Query response:', r.json())
            break
        else:
            print('Query failed:', r.text[:200])
    except Exception as e:
        print('Query exception:', e)
print('Done')
