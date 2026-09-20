"""Disease prediction router: POST /api/disease/predict (image upload).

Uses the real pre-trained PlantVillage model (serverless) with automatic
fallback to the deterministic mock when the API is unavailable.
Set USE_REAL_DISEASE_MODEL=false in .env to force mock (offline demo).
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from backend.config import settings
from backend.schemas import DiseasePredictResponse, DiseasePredictionResult
from backend.services import disease_service
from backend.utils.image_utils import validate_image, save_upload

router = APIRouter()


@router.post("/predict", response_model=DiseasePredictResponse)
async def predict(image: UploadFile = File(...),
                  crop: Optional[str] = Form(None),
                  symptoms: Optional[str] = Form(None)):
    # Validate MIME + size
    if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, f"Invalid image type {image.content_type}. Use JPG/PNG/WebP.")
    data = await image.read()
    if len(data) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, "Image too large (max 10 MB).")
    ok, msg = validate_image(data)
    if not ok:
        raise HTTPException(400, f"Invalid image: {msg}")
    # Save for audit (best-effort)
    try:
        save_upload(data, image.filename or "crop.jpg", subdir="images")
    except Exception:
        pass

    res = await disease_service.predict_real(data, crop_hint=crop)
    preds = [DiseasePredictionResult(disease_name=p["disease_name"], confidence=p["confidence"]) for p in res["predictions"]]
    return DiseasePredictResponse(
        predictions=preds, top_prediction=preds[0],
        symptoms_observed=res.get("symptoms_observed"),
        ai_analysis=res["ai_analysis"],
        recommended_actions=res["recommended_actions"],
        preventive_measures=res["preventive_measures"],
        warning=res.get("warning"),
        confidence_threshold=res["confidence_threshold"],
        model=res.get("model"),
        display=res.get("display"),
    )