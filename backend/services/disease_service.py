"""
Mock disease detection service (prototype).

- Deterministic mock: picks prediction from image hash so demos are stable.
- Output schema IDENTICAL to real CNN service -> one-line swap later:
    from ai.crop_disease import get_disease_model  # real model
- Never presents uncertain prediction as confirmed diagnosis.
- Confidence < 0.60 -> strong warning + ask expert.
"""

import hashlib
import structlog
from typing import Optional

from backend.config import settings
from backend.data.diseases import DISEASE_CATALOG, DISEASE_INFO
from backend.ai.disease_inference import remote_predict, build_result

logger = structlog.get_logger()
CONFIDENCE_THRESHOLD = 0.60

# Candidate mock classes (subset, realistic for demo)
MOCK_CLASSES = [
    "Tomato_Early_blight", "Tomato_Late_blight", "Potato_Late_blight",
    "Wheat_Leaf_rust", "Rice_Blast", "Cotton_Leaf_Curl_Virus", "Healthy",
]


def predict_mock(image_bytes: bytes, crop_hint: Optional[str] = None, top_k: int = 3) -> dict:
    """Deterministic mock prediction from image bytes."""
    h = int(hashlib.md5(image_bytes).hexdigest(), 16)

    # If crop hint given, prefer matching class for realistic demo
    candidates = MOCK_CLASSES
    if crop_hint:
        ch = crop_hint.lower()
        matched = [c for c in MOCK_CLASSES if ch in c.lower()]
        if matched:
            candidates = matched + [c for c in MOCK_CLASSES if c not in matched]

    primary_idx = h % len(candidates)
    primary = candidates[primary_idx]
    # Confidence derived from hash: 0.45 - 0.95 range (so low-conf cases occur)
    conf = 0.45 + (h % 51) / 100.0

    predictions = [{"disease_name": primary, "confidence": round(conf, 2)}]
    for i in range(1, top_k):
        alt = candidates[(primary_idx + i) % len(candidates)]
        c = max(0.05, round(conf - 0.15 * i - (h % 7) / 100.0, 2))
        predictions.append({"disease_name": alt, "confidence": c})

    info = DISEASE_INFO.get(primary, {})
    crop = info.get("crop", "unknown")
    low_conf = conf < CONFIDENCE_THRESHOLD

    if primary == "Healthy":
        analysis = "Plant appears healthy. No clear disease symptoms detected. Continue monitoring."
    else:
        analysis = (
            f"Possible {primary.replace('_', ' ')} on {crop} "
            f"(confidence {conf:.0%}). Symptoms: {info.get('symptoms', 'N/A')}"
        )
        if low_conf:
            analysis += " UNCERTAIN - do NOT treat as confirmed. Get expert inspection."

    warning = None
    if low_conf:
        warning = (
            f"Low confidence ({conf:.0%}). This is NOT a confirmed diagnosis. "
            "Please consult an agricultural expert before spraying."
        )

    return {
        "predictions": predictions,
        "top_prediction": predictions[0],
        "crop": crop,
        "symptoms_observed": info.get("symptoms"),
        "ai_analysis": analysis,
        "recommended_actions": _actions(info, low_conf),
        "preventive_measures": _split(info.get("prevention", "Follow good practices.")),
        "warning": warning,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "model": "mock-v1 (swap with CNN for production)",
    }


def _actions(info: dict, low_conf: bool) -> list:
    base = _split(info.get("treatment", "Consult extension officer."))
    if low_conf:
        return ["DO NOT spray based on this uncertain result alone.", "Get field inspection by expert."] + base
    return base


def _split(text: str) -> list:
    parts = [p.strip(" .") for p in text.replace(";", ",").split(",")]
    items = [p for p in parts if p]
    return items if items else [text]


# ---------------------------------------------------------------- real model
async def predict_real(image_bytes: bytes, crop_hint: Optional[str] = None,
                       top_k: int = 3, force_mock: bool = False) -> dict:
    """Real pre-trained PlantVillage model (serverless) with deterministic mock fallback.

    Response shape identical to predict_mock - frontend/API unchanged.
    `model` field tells which engine produced the result.
    """
    if force_mock or not getattr(settings, "USE_REAL_DISEASE_MODEL", True):
        return predict_mock(image_bytes, crop_hint, top_k)

    try:
        raw = await remote_predict(image_bytes, top_k)
        if not raw:
            logger.warning("remote predict empty, falling back to mock")
            res = predict_mock(image_bytes, crop_hint, top_k)
            res["model"] = "mock-fallback (remote unavailable)"
            return res
        results = [build_result(p, crop_hint) for p in raw]
        # Keep top_k, filter junk (unknown malformed labels)
        results = [r for r in results if r["disease_name"] != "unknown"][:top_k]
        if not results:
            return predict_mock(image_bytes, crop_hint, top_k)
        top = results[0]
        return {
            "predictions": [{"disease_name": r["disease_name"], "confidence": r["confidence"]} for r in results],
            "top_prediction": {"disease_name": top["disease_name"], "confidence": top["confidence"]},
            "crop": top["crop"],
            "display": top["display"],
            "symptoms_observed": top["symptoms_observed"],
            "ai_analysis": top["analysis"],
            "recommended_actions": top["recommended_actions"],
            "preventive_measures": top["preventive_measures"],
            "warning": top["warning"],
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "model": "plantvillage-mobilenetv2 (serverless)",
        }
    except Exception as e:
        logger.warning("predict_real crashed, mock fallback", error=str(e))
        res = predict_mock(image_bytes, crop_hint, top_k)
        res["model"] = "mock-fallback (error)"
        return res
