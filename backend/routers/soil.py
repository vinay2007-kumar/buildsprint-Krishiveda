"""Soil router: POST /api/soil/analyze."""

from fastapi import APIRouter
from backend.schemas import SoilAnalysisCreate, SoilRecommendationResponse
from backend.services import soil_service

router = APIRouter()


@router.post("/analyze", response_model=SoilRecommendationResponse)
async def analyze(body: SoilAnalysisCreate):
    # schemas uses crop_id; accept crop name via context is frontend concern.
    # For prototype: map common crop_id -> name (1=wheat default).
    crop_map = {1: "wheat", 2: "rice", 3: "maize", 4: "cotton", 5: "sugarcane",
                6: "soybean", 7: "groundnut", 8: "mustard", 9: "tomato", 10: "potato"}
    crop = crop_map.get(body.crop_id or 1, "wheat")
    res = soil_service.analyze_soil(
        crop=crop, soil_type=body.soil_type.value if hasattr(body.soil_type, "value") else str(body.soil_type),
        ph=body.ph, nitrogen=body.nitrogen, phosphorus=body.phosphorus, potassium=body.potassium,
        growth_stage=body.growth_stage.value if body.growth_stage and hasattr(body.growth_stage, "value") else (str(body.growth_stage) if body.growth_stage else None),
    )
    return SoilRecommendationResponse(**res)
