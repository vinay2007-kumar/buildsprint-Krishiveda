"""Probe HF router OpenAI-compatible chat endpoint."""
import asyncio, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings

CANDIDATES = ["Qwen/Qwen2.5-7B-Instruct", "HuggingFaceH4/zephyr-7b-beta",
              "mistralai/Mistral-7B-Instruct-v0.3", "meta-llama/Llama-3.1-8B-Instruct"]

async def probe(model):
    url = "https://router.huggingface.co/v1/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.post(url, headers={"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"},
                             json={"model": model, "messages": [{"role": "user", "content": "Say OK"}],
                                   "max_tokens": 10})
        print(f"{r.status_code}  {model}  :: {r.text[:200].replace(chr(10), ' ')}")
        return r.status_code
    except Exception as e:
        print(f"ERR  {model}  :: {e}")
        return -1

async def main():
    for m in CANDIDATES:
        if await probe(m) == 200:
            print("FIRST WORKING MODEL:", m)
            break

asyncio.run(main())
