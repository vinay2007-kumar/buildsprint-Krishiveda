"""Probe which free models are served on HF Inference Providers."""
import asyncio, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings

CANDIDATES = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "Qwen/Qwen2.5-7B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "microsoft/Phi-3-mini-4k-instruct",
    "google/gemma-2-9b-it",
    "meta-llama/Meta-Llama-3-8B-Instruct",
]

async def probe(model):
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    try:
        async with httpx.AsyncClient(timeout=60.0) as c:
            r = await c.post(url, headers={"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"},
                             json={"inputs": "Say OK", "parameters": {"max_new_tokens": 5}})
        body = r.text[:150].replace("\n", " ")
        print(f"{r.status_code}  {model}  :: {body}")
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
