import sys, json, traceback
from pathlib import Path

# Usage: python flan_worker.py payload.json
if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"error": "No payload file provided"}))
            sys.exit(2)
        payload_path = Path(sys.argv[1])
        payload = json.loads(payload_path.read_text())
        prompt = payload.get('prompt', '')
        max_new_tokens = payload.get('max_new_tokens', 256)

        # Resolve model path relative to project root
        project_root = Path(__file__).resolve().parents[1]
        model_path = project_root / 'src' / 'agents' / 'rag_system' / 'models' / 'flan-t5-small'

        from transformers import pipeline
        qa = pipeline('text2text-generation', model=str(model_path), device=-1)

        out = qa(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        # out is a list of dicts
        generated_text = out[0].get('generated_text', '') if out else ''

        print(json.dumps({"generated_text": generated_text}))
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(json.dumps({"error": str(e)}))
        sys.exit(3)
