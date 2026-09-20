"""Live endpoint test for KrishiVeda backend (run with TestClient, no server needed)."""
import sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")

from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app, raise_server_exceptions=False)

checks = []

def check(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name, detail)

r = c.get("/health")
check("GET /health", r.status_code == 200, r.text[:120])

r = c.get("/")
check("GET /", r.status_code == 200 and "KrishiVeda" in r.text, r.text[:120])

r = c.get("/api/crops")
check("GET /api/crops", r.status_code == 200 and "wheat" in r.text, r.text[:120])

r = c.post("/api/chat", json={"message": "Why are wheat leaves yellow?", "language": "en"})
check("POST /api/chat", r.status_code == 200 and "response" in r.text, r.text[:200])

r = c.post("/api/soil/analyze", json={"soil_type": "black", "ph": 7.0, "nitrogen": 40,
                                      "phosphorus": 30, "potassium": 30, "growth_stage": "vegetative"})
check("POST /api/soil/analyze", r.status_code == 200 and "soil_health_score" in r.text, r.text[:200])

r = c.get("/api/weather", params={"lat": 23.03, "lon": 72.58})
check("GET /api/weather", r.status_code == 200, r.text[:200])

# Disease: fake image bytes (PIL not installed -> validation fails gracefully with 400, not 500)
r = c.post("/api/disease/predict", files={"image": ("leaf.jpg", b"not-an-image", "image/jpeg")})
check("POST /api/disease/predict invalid image -> 400", r.status_code == 400, r.text[:150])

r = c.get("/api/scheme/list")
check("GET /api/scheme/list", r.status_code == 200, r.text[:120])

print()
failed = [n for n, ok in checks if not ok]
print("RESULT:", "ALL PASS" if not failed else f"FAILED: {failed}")
sys.exit(1 if failed else 0)
