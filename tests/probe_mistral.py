"""Probe Mistral + light models on HF chat router (max_tokens tiny)."""
import asyncio, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings

CANDIDATES = [
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-7B-v0.3",
    "google/gemma-2-2b-it",
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
]

async def probe(model):
    url = "https://router.huggingface.co/v1/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.post(url, headers={"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"},
                             json={"model": model, "messages": [{"role": "user", "content": "Reply with OK"}],
                                   "max_tokens": 10})
        err = ""
        if r.status_code != 200:
            try:
                err = r.json()["error"]["message"][:90]
            except Exception:
                err = r.text[:90]
        print(f"{r.status_code}  {model}  :: {err}")
        return r.status_code
    except Exception as e:
        print(f"ERR  {model}  :: {e}")
        return -1

async def main():
    results = await asyncio.gather(*[probe(m) for m in CANDIDATES])
    ok = [m for m, s in zip(CANDIDATES, results) if s == 200]
    print()
    print("WORKING MODELS:", ok if ok else "none (see errors above)")

asyncio.run(main())