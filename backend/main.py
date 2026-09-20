"""
KrishiVeda - AI-powered agricultural assistant for smallholder farmers.
FastAPI application entry point.

Modules:
- Disease detection (mock vision model, swappable for real CNN)
- Conversational AI assistant (HuggingFace Inference API)
- Soil & fertilizer recommendations (rule-based engine + LLM)
- Weather-aware irrigation advice (Open-Meteo, no API key)
- Government scheme RAG (PDF -> ChromaDB -> LLM)
- Voice interaction (STT/TTS with browser + backend fallback)
- Multilingual: English, Hindi, Gujarati
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from backend.config import settings
from backend.routers import disease, chat, soil, weather, scheme, voice

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # Ensure upload directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "audio"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "schemes"), exist_ok=True)

    # Try to init DB (non-fatal for demo if DB unavailable)
    try:
        from backend.database import init_db
        await init_db()
        logger.info("Database ready")
    except Exception as e:
        logger.warning("DB init skipped (demo mode ok)", error=str(e))

    logger.info("KrishiVeda starting", version=settings.APP_VERSION)
    yield
    try:
        from backend.database import close_db
        await close_db()
    except Exception:
        pass
    logger.info("KrishiVeda shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Voice-first AI assistant for smallholder farmers.",
    lifespan=lifespan,
)

# CORS - permissive for hackathon demo (tighten in production)
# Note: "*" + allow_credentials=True is rejected by browsers, so expand specificity.
_cors_origins = [o for o in settings.CORS_ORIGINS if o != "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["*"],
    allow_credentials=bool(_cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded images / generated audio (ensure dirs exist at import so mount never skipped)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(disease.router, prefix="/api/disease", tags=["Disease"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(soil.router, prefix="/api/soil", tags=["Soil"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(scheme.router, prefix="/api/scheme", tags=["Schemes"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])


@app.get("/", tags=["Health"])
async def root():
    """Root - basic info."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "modules": ["disease", "chat", "soil", "weather", "scheme", "voice"],
        "languages": ["en", "hi", "gu"],
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check for deployment / monitoring."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/api/crops", tags=["Meta"])
async def list_crops():
    """List supported crops (static seed, DB-backed in full version)."""
    from backend.data.crops import CROPS
    return {"success": True, "data": CROPS}


@app.get("/api/diseases", tags=["Meta"])
async def list_diseases():
    """List known diseases with symptoms/treatment."""
    from backend.data.diseases import DISEASE_CATALOG
    return {"success": True, "data": DISEASE_CATALOG}


@app.get("/api/languages", tags=["Meta"])
async def list_languages():
    """Supported UI / voice languages."""
    return {
        "success": True,
        "data": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "hi", "name": "Hindi", "native": "हिंदी"},
            {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી"},
        ],
    }
