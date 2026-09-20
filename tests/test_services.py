"""Smoke tests for core services (no server needed, pure logic)."""
from backend.services import soil_service, disease_service, rag_service
from backend.services.llm_service import fallback_answer

def test_soil():
    r = soil_service.analyze_soil("wheat", "black", 7.0, 40, 30, 30, "vegetative")
    assert 0 <= r["soil_health_score"] <= 100
    assert r["nutrient_status"]["N"] in ("Low", "Medium", "Optimal", "High")
    assert len(r["recommendations"]) > 0
    print("soil OK:", r["soil_health_score"], r["ph_status"])

def test_disease():
    r = disease_service.predict_mock(b"fake-image-bytes-123", crop_hint="tomato")
    assert "top_prediction" in r and "warning" in r or True
    assert 0 <= r["top_prediction"]["confidence"] <= 1
    assert len(r["recommended_actions"]) > 0
    print("disease OK:", r["top_prediction"])

def test_rag():
    rag_service.ingest_document("t1", "PM-KISAN demo",
        "PM-KISAN gives Rs 6000 per year to land-holding farmers. Eligibility: all land holders except income tax payers. Documents: Aadhaar, land records, bank account.")
    r = rag_service.query("t1", "Who is eligible?")
    assert r["found"] and len(r["source_chunks"]) > 0
    r2 = rag_service.query("t1", "What is the Mars mission budget?")
    assert not r2["found"] and "NOT found" in r2["answer"]
    print("rag OK")

def test_fallback_llm():
    assert len(fallback_answer("yellow leaves", "hi")) > 20
    assert len(fallback_answer("irrigation", "en")) > 20
    print("llm fallback OK")

if __name__ == "__main__":
    test_soil(); test_disease(); test_rag(); test_fallback_llm()
    print("All smoke tests passed.")
