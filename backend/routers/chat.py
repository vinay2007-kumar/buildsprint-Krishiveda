"""Chat router: POST /api/chat + GET /api/chat/history (stub)."""

from fastapi import APIRouter
from backend.schemas import ChatRequest, ChatResponse
from backend.services import chat_service

router = APIRouter()

_HISTORY: list = []  # in-memory demo history (DB-backed in full version)


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    res = await chat_service.chat(req.message, language=req.language.value if hasattr(req.language, "value") else str(req.language),
                                  session_id=req.session_id, context=req.context)
    _HISTORY.append({"role": "user", "content": req.message, "session_id": res["session_id"]})
    _HISTORY.append({"role": "assistant", "content": res["response"], "session_id": res["session_id"]})
    return ChatResponse(response=res["response"], language=res["language"],
                        session_id=res["session_id"], metadata=res.get("metadata"),
                        confidence=res.get("confidence"))


@router.get("/history")
async def history(session_id: str = "", limit: int = 20):
    items = [h for h in _HISTORY if not session_id or h.get("session_id") == session_id]
    return {"success": True, "data": items[-limit:]}
