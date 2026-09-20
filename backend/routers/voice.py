"""Voice router: transcribe + speak with fallbacks."""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from backend.config import settings
from backend.services import voice_service

router = APIRouter()


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), language: Optional[str] = Form(None)):
    suffix = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"
    tmp = os.path.join(settings.UPLOAD_DIR, "audio", f"in_{uuid.uuid4().hex[:8]}{suffix}")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(await audio.read())
    res = await voice_service.transcribe(tmp, language)
    return {"success": True, "data": res}


@router.post("/speak")
async def speak(text: str = Form(...), language: str = Form("hi")):
    res = await voice_service.speak(text, language)
    return {"success": True, "data": res}
