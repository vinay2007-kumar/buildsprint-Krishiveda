"""End-to-end scheme pipeline: build a valid text PDF, upload, query."""
import io, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")

from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app, raise_server_exceptions=False)

# Valid text PDF generated via reportlab (see test setup); read from disk
with open(r"C:\Users\vinay\AppData\Local\Temp\opencode\pmkisan.pdf", "rb") as f:
    pdf_bytes = f.read()

r = c.post("/api/scheme/upload", files={"file": ("pmkisan.pdf", pdf_bytes, "application/pdf")},
           data={"title": "PM-KISAN"})
print("UPLOAD:", r.status_code, r.text[:300])
assert r.status_code == 200, r.text
doc_id = r.json()["data"]["doc_id"]

r = c.post("/api/scheme/query", json={"document_id": doc_id, "question": "Who is eligible?", "language": "en"})
print("QUERY eligible:", r.status_code, r.text[:300])
assert r.status_code == 200 and "land holders" in r.text

r = c.post("/api/scheme/query", json={"document_id": doc_id, "question": "Mars mission budget?", "language": "en"})
print("QUERY mars:", r.status_code, r.text[:300])
assert r.status_code == 200 and "NOT found" in r.text

r = c.post("/api/scheme/upload", files={"file": ("x.txt", b"hello", "text/plain")}, data={"title": "bad"})
print("UPLOAD non-pdf:", r.status_code)
assert r.status_code == 400

print("SCHEME PIPELINE ALL PASS")
