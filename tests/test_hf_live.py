"""Live HF test: verifies token works and chatbot uses real LLM (not fallback)."""
import asyncio, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")

from backend.services import llm_service

async def main():
    res = await llm_service.generate_response("Why are my wheat leaves turning yellow?", language="en")
    print("SOURCE:", res["source"])
    print("CONFIDENCE:", res["confidence"])
    print("TEXT:", res["text"][:600])
    assert res["source"] == "huggingface", f"Still on fallback: {res['source']}"
    print("LIVE HF TEST PASS")

asyncio.run(main())
