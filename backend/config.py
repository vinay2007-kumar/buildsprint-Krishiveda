import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "KrishiVeda"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./krishiveda.db"
    # For PostgreSQL: postgresql+asyncpg://user:pass@localhost/krishiveda

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    # AI/ML (HuggingFace primary per project decision)
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    DISEASE_MODEL_PATH: str = "./models/crop_disease_model.pth"
    USE_MOCK_DISEASE_MODEL: bool = True  # prototype: mock; set False to use ai/crop_disease.py CNN
    USE_REAL_DISEASE_MODEL: bool = True  # pre-trained PlantVillage (serverless); mock on failure
    DISEASE_MODEL: str = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL: str = "meta-llama/Llama-3.1-8B-Instruct"  # via HuggingFace Inference Providers (chat API)

    # Weather API (Open-Meteo: free, no key)
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_API_URL: str = "https://api.open-meteo.com/v1/forecast"

    # Voice
    STT_MODEL: str = "openai/whisper-small"
    TTS_LANGUAGE_MAP: dict = {
        "en": "en",
        "hi": "hi",
        "gu": "gu"
    }
    # ElevenLabs (TTS/STT) — primary when a key is present; falls back to edge-tts/gTTS/browser
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # "Rachel" multilingual default; set a Hindi voice (e.g. Kriya) per demo
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    ELEVENLABS_STT_MODEL: str = "scribe_v1"

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_DOC_TYPES: list = ["application/pdf"]

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8501", "*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()