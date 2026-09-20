"""
Soil recommendation engine - rule-based NPK + pH + crop + growth stage.

Outputs SoilRecommendationResponse-compatible dict:
soil_health_score, nutrient_status, ph_status, recommendations, amendments, advice.
"""

from typing import Optional

# Ideal NPK (kg/ha) reference per crop (simplified, extension-officer guidance level)
CROP_NPK = {
    "wheat": {"N": 120, "P": 60, "K": 40},
    "rice": {"N": 120, "P": 60, "K": 60},
    "maize": {"N": 120, "P": 60, "K": 40},
    "cotton": {"N": 120, "P": 60, "K": 60},
    "sugarcane": {"N": 250, "P": 115, "K": 115},
    "soybean": {"N": 30, "P": 75, "K": 40},
    "groundnut": {"N": 25, "P": 50, "K": 75},
    "mustard": {"N": 80, "P": 40, "K": 40},
    "tomato": {"N": 100, "P": 50, "K": 50},
    "potato": {"N": 120, "P": 80, "K": 100},
    "onion": {"N": 100, "P": 50, "K": 50},
    "chilli": {"N": 100, "P": 50, "K": 50},
}

STAGE_FACTOR = {
    "seedling": 0.3, "vegetative": 0.7, "flowering": 1.0,
    "fruiting": 0.9, "maturity": 0.4, "harvest": 0.1, None: 1.0,
}


def analyze_soil(crop: Optional[str], soil_type: str, ph: float,
                 nitrogen: float, phosphorus: float, potassium: float,
                 growth_stage: Optional[str] = None) -> dict:
    crop_key = (crop or "wheat").lower()
    need = CROP_NPK.get(crop_key, CROP_NPK["wheat"])
    factor = STAGE_FACTOR.get(growth_stage, 1.0)

    def status(val, req):
        ratio = val / max(req * factor, 1)
        if ratio < 0.5: return "Low"
        if ratio < 0.85: return "Medium"
        if ratio <= 1.25: return "Optimal"
        return "High"

    n_s, p_s, k_s = status(nitrogen, need["N"]), status(phosphorus, need["P"]), status(potassium, need["K"])

    if ph < 5.5: ph_status = "Strongly Acidic"
    elif ph < 6.5: ph_status = "Slightly Acidic"
    elif ph <= 7.5: ph_status = "Neutral"
    elif ph <= 8.5: ph_status = "Slightly Alkaline"
    else: ph_status = "Strongly Alkaline"

    # Health score: weighted nutrient + pH penalty
    score = 100.0
    for s in (n_s, p_s, k_s):
        if s == "Low": score -= 18
        elif s == "Medium": score -= 8
        elif s == "High": score -= 5
    if ph_status in ("Strongly Acidic", "Strongly Alkaline"): score -= 15
    elif ph_status in ("Slightly Acidic", "Slightly Alkaline"): score -= 5
    score = max(5, min(100, round(score, 1)))

    recs = []
    if n_s in ("Low", "Medium"):
        deficit = max(0, need["N"] * factor - nitrogen)
        urea = round(deficit / 0.46, 1)  # urea 46% N
        if urea > 0:
            recs.append({"fertilizer_name": "Urea (46% N)", "nutrient_content": {"N": 46, "P": 0, "K": 0},
                         "dosage_per_acre": round(urea * 0.4047, 1), "application_method": "top_dressing",
                         "timing": "Split in 2 doses, after irrigation", "cost_estimate": None})
    if p_s in ("Low", "Medium"):
        deficit = max(0, need["P"] * factor - phosphorus)
        dap = round(deficit / 0.46, 1)  # DAP 18-46-0 approx for P
        if dap > 0:
            recs.append({"fertilizer_name": "DAP (18-46-0)", "nutrient_content": {"N": 18, "P": 46, "K": 0},
                         "dosage_per_acre": round(dap * 0.4047, 1), "application_method": "basal",
                         "timing": "At sowing / transplanting", "cost_estimate": None})
    if k_s in ("Low", "Medium"):
        deficit = max(0, need["K"] * factor - potassium)
        mop = round(deficit / 0.60, 1)
        if mop > 0:
            recs.append({"fertilizer_name": "MOP (60% K2O)", "nutrient_content": {"N": 0, "P": 0, "K": 60},
                         "dosage_per_acre": round(mop * 0.4047, 1), "application_method": "basal",
                         "timing": "At sowing with DAP", "cost_estimate": None})
    if not recs:
        recs.append({"fertilizer_name": "No major fertilizer needed", "nutrient_content": {"N": 0, "P": 0, "K": 0},
                     "dosage_per_acre": 0, "application_method": "none",
                     "timing": "Maintain FYM 2-4 t/acre per season", "cost_estimate": 0})

    amendments, advice = [], []
    if ph < 5.5:
        amendments.append("Apply agricultural lime 200-400 kg/acre (soil-test based).")
        advice.append("Acidic soil locks phosphorus. Lime + FYM improves uptake.")
    elif ph > 8.0:
        amendments.append("Apply gypsum 200-300 kg/acre + green manure (dhaincha).")
        advice.append("Alkaline soil: prefer drip, avoid waterlogging, add organic matter.")
    if soil_type in ("sandy",):
        amendments.append("Add FYM/compost 4-5 t/acre to improve water holding.")
    if soil_type in ("clay", "black"):
        advice.append("Heavy soil: ensure drainage, avoid irrigation before rain.")
    advice.append("Re-test soil every season. This is guidance, not guaranteed yield.")
    advice.append(f"Stage '{growth_stage or 'general'}': split nitrogen for best efficiency.")

    return {
        "soil_health_score": score,
        "nutrient_status": {"N": n_s, "P": p_s, "K": k_s},
        "ph_status": ph_status,
        "recommendations": recs,
        "soil_amendments": amendments,
        "general_advice": advice,
    }
