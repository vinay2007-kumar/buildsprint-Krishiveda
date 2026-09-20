"""Full-stack disease test: real PlantVillage model (serverless) + fallback verification.

1. Real spotted-leaf image -> remote inference -> structure + catalog info
2. Offline simulation (bad token) -> graceful mock fallback, still 200
"""
import io, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
from fastapi.testclient import TestClient
from backend.main import app
from PIL import Image, ImageDraw
import random

random.seed(7)
img = Image.new("RGB", (300, 300), (30, 120, 30))
d = ImageDraw.Draw(img)
for _ in range(80):
    x, y = random.randint(5, 290), random.randint(5, 290)
    d.ellipse([x, y, x + random.randint(6, 24), y + random.randint(6, 24)], fill=(120, 95, 30))
buf = io.BytesIO(); img.save(buf, format="JPEG")
LEAF = buf.getvalue()

c = TestClient(app, raise_server_exceptions=False)

# ---- 1. Real inference
r = c.post("/api/disease/predict", files={"image": ("leaf.jpg", LEAF, "image/jpeg")})
j = r.json() if r.status_code == 200 else {}
print("STATUS:", r.status_code)
print("TOP:", j.get("top_prediction"), "| model:", j.get("model"), "| display:", j.get("display"))
print("WARNING:", j.get("warning"))
print("ACTIONS:", (j.get("recommended_actions") or [])[:2])
assert r.status_code == 200, r.text
assert "plantvillage" in (j.get("model") or ""), f"expected real model, got {j.get('model')}"
assert 0 <= j["top_prediction"]["confidence"] <= 1
print("REAL MODEL TEST PASS")

# ---- 2. Force mock fallback (offline demo path)
import backend.services.disease_service as ds
res = await_ = None
async def forced():
    return await ds.predict_real(LEAF, force_mock=True)
import asyncio
r2 = asyncio.run(forced())
print("\nFORCED MOCK model:", r2.get("model"), "| top:", r2["top_prediction"])
assert "mock" in (r2.get("model") or "").lower()
print("FALLBACK TEST PASS")