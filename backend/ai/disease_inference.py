"""
Real crop-disease inference via HuggingFace Inference Providers (serverless).

Uses a PRE-TRAINED PlantVillage model (MobileNetV2, 38 classes) - no training needed:
    DISEASE_MODEL = linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification

Flow:
    image bytes -> HF serverless image-classification -> top-k (label, score)
    -> normalize label -> match built-in catalog (symptoms/treatment/prevention)
    -> build full response (same shape as mock) with confidence warnings.

Honesty rules:
    - class not in catalog -> generic expert-consult advice, clearly labeled
    - confidence < 60% -> strong warning, never a confirmed diagnosis
    - any API failure is caught by the caller and falls back to the deterministic mock.
"""

import re
import structlog
from typing import Optional

from backend.config import settings
from backend.data.diseases import DISEASE_INFO

logger = structlog.get_logger()
CONFIDENCE_THRESHOLD = 0.60

_CROP_TOKENS = [
    "tomato", "potato", "corn", "maize", "pepper", "apple", "grape",
    "strawberry", "peach", "cherry", "soybean", "soyabean", "squash",
    "blueberry", "orange", "raspberry", "wheat", "rice", "cotton",
]

# Ordered longest-first so "yellow leaf curl" matches before "leaf"
_DISEASE_ALIASES = [
    ("yellow leaf curl", "Yellow_Leaf_Curl_Virus"),
    ("septoria", "Septoria_leaf_spot"),
    ("target spot", "Target_Spot"),
    ("early blight", "Early_blight"),
    ("late blight", "Late_blight"),
    ("bacterial spot", "Bacterial_spot"),
    ("leaf mold", "Leaf_Mold"),
    ("spider mite", "Spider_mites"),
    ("mosaic", "mosaic_virus"),
    ("leaf rust", "Leaf_rust"),
    ("stem rust", "Stem_rust"),
    ("blast", "Blast"),
    ("leaf curl", "Leaf_Curl_Virus"),
    ("common rust", "Common_Rust"),
    ("gray leaf spot", "Gray_Leaf_Spot"),
    ("grey leaf spot", "Gray_Leaf_Spot"),
    ("northern leaf blight", "Northern_Leaf_Blight"),
    ("powdery mildew", "Powdery_mildew"),
    ("black rot", "Black_rot"),
    ("cedar apple rust", "Cedar_Apple_Rust"),
    ("apple scab", "Apple_Scab"),
    ("leaf scorch", "Leaf_Scorch"),
    ("esca", "Esca"),
    ("leaf blight", "Leaf_blight"),
    ("citrus greening", "Citrus_Greening"),
    ("healthy", "Healthy"),
]


def _clean(label: str) -> str:
    """Normalize label separators: 'Tomato___Early_blight' / 'Tomato with Early Blight'."""
    return label.replace("___", " ").replace("_", " ").replace("(", " ").replace(")", " ")


def _canonical_key(label: str) -> Optional[str]:
    """Map a model label to our catalog key, e.g. 'Tomato with Early Blight' -> 'Tomato_Early_blight'."""
    s = _clean(label).lower()
    s = re.sub(r"\bwith\b|\bhave\b|\bhas\b", " ", s)  # 'Corn (Maize) with Common Rust'
    crop = next((c for c in _CROP_TOKENS if c in s), None)
    if crop in ("maize",):  # normalize maize -> corn in catalog keys
        crop = "corn"
    if crop is None or crop == "soyabean":
        crop = "soybean"
    for alias, disease in _DISEASE_ALIASES:
        if alias in s:
            key = f"{crop.capitalize()}_{disease}" if crop else disease
            return key if key in DISEASE_INFO else None
    return None


def build_result(prediction: dict, crop_hint: Optional[str] = None) -> dict:
    """Convert one (label, score) from the model into a full actionable result."""
    label = prediction.get("label", "Unknown")
    score = float(prediction.get("score", 0.0))
    key = _canonical_key(label)
    info = DISEASE_INFO.get(key, {}) if key else {}
    crop = info.get("crop") or "unknown"
    disease = info.get("disease") or key or label
    display = label.replace("_", " ")
    low_conf = score < CONFIDENCE_THRESHOLD

    if info.get("disease") == "Healthy":
        analysis = "Plant appears healthy. No clear disease symptoms detected. Continue normal care."
    elif info:
        analysis = (
            f"Model says: possible {display} on {crop} "
            f"(confidence {score:.0%}). Symptoms: {info.get('symptoms', 'N/A')}"
        )
        if low_conf:
            analysis += " UNCERTAIN - do NOT treat as confirmed."
    else:
        analysis = (
            f"Model detected '{display}' (confidence {score:.0%}). "
            "This class is not in the offline advisory catalog - "
            "do NOT self-diagnose. Get a field inspection by a local extension officer."
        )

    actions = [a.strip() for a in info.get("treatment", "").split(",") if a.strip()] if info else [
        "Do NOT spray based on this result alone.",
        "Invite a KVK / agriculture officer to inspect the field.",
        "If the officer confirms, they will prescribe the exact chemical and dose.",
    ]
    if low_conf and info:
        actions = ["Do NOT spray on this uncertain result alone - get expert verification."] + actions
    prevention = [a.strip() for a in info.get("prevention", "").split(",") if a.strip()] if info else [
        "Regular field scouting (twice a week).",
        "Balanced fertilization and irrigation.",
        "Use trusted seed/seedlings from certified sources.",
    ]
    warning = None
    if low_conf:
        warning = (
            f"Low confidence ({score:.0%}). This is NOT a confirmed diagnosis. "
            "Consult an agricultural expert before treating."
        )
    return {
        "disease_name": disease,
        "confidence": round(score, 2),
        "crop": crop,
        "display": display,
        "symptoms_observed": info.get("symptoms") if info else None,
        "analysis": analysis,
        "recommended_actions": actions,
        "preventive_measures": prevention,
        "warning": warning,
    }


async def remote_predict(image_bytes: bytes, top_k: int = 3) -> list:
    """Call HF serverless image-classification; returns top-k dicts, [] on failure."""
    model = getattr(settings, "DISEASE_MODEL", "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification")
    token = getattr(settings, "HUGGINGFACE_TOKEN", None)
    if not token:
        return []
    try:
        import httpx
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        async with httpx.AsyncClient(timeout=60.0) as c:
            r = await c.post(url, headers={
                "Authorization": f"Bearer {token}", "Content-Type": "image/jpeg",
            }, content=image_bytes)
        if r.status_code != 200:
            logger.warning("disease model non-200", status=r.status_code, body=r.text[:150])
            return []
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning("disease remote inference failed", error=str(e))
        return []