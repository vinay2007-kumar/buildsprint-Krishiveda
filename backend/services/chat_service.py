"""
Chat service: builds agricultural context prompt, calls LLM, farmer-friendly post-process.

Context (optional): crop, soil_type, growth_stage, location, weather summary.
Stores nothing by default (DB history added when auth wired); returns session_id.
"""

import uuid
import structlog
from typing import Optional

from backend.services import llm_service

logger = structlog.get_logger()


async def chat(message: str, language: str = "hi", session_id: Optional[str] = None,
               context: Optional[dict] = None) -> dict:
    sid = session_id or str(uuid.uuid4())[:8]
    ctx_txt = ""
    if context:
        bits = []
        for k in ("crop", "soil_type", "growth_stage", "location", "weather"):
            if context.get(k):
                bits.append(f"{k}={context[k]}")
        if bits:
            ctx_txt = "Context: " + ", ".join(bits) + ". Use it in advice. "
    prompt = f"{ctx_txt}Question: {message}"
    try:
        res = await llm_service.generate_response(prompt, language=language)
        text = res["text"]
    except Exception as e:
        logger.warning("chat LLM failed", error=str(e))
        res = {"source": "fallback", "confidence": 0.4}
        text = llm_service.fallback_answer(message, language if language in ("en", "hi", "gu") else "hi")
    # Farmer-friendly: cap length for voice readability
    if len(text) > 900:
        text = text[:880].rsplit(".", 1)[0] + "."
    return {"response": text, "language": language, "session_id": sid,
            "metadata": {"source": res.get("source"), "context_used": bool(ctx_txt)},
            "confidence": res.get("confidence", 0.6)}
