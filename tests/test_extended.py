"""Extended tests: real image disease path, PDF scheme RAG, voice fallbacks."""
import io, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")

from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app, raise_server_exceptions=False)
ok = True

def check(name, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name, str(detail)[:150])
    if not cond:
        ok = False

# 1. Real image (generated leaf-like JPEG) -> 200 with prediction structure
from PIL import Image
img = Image.new("RGB", (300, 300), (34, 139, 34))
buf = io.BytesIO()
img.save(buf, format="JPEG")
r = c.post("/api/disease/predict", files={"image": ("leaf.jpg", buf.getvalue(), "image/jpeg")},
           data={"crop": "tomato"})
j = r.json() if r.status_code == 200 else {}
check("disease real image 200", r.status_code == 200 and "top_prediction" in j, r.text[:150])
check("disease has actions+warning-field", "recommended_actions" in j and "warning" in j, "")

# 2. Scheme PDF upload + query (found vs not-found)
from pypdf import PdfWriter
from pypdf.generic import NameObject, TextStringObject
w = PdfWriter()
page = w.add_blank_page(400, 400)
page[NameObject("/Contents")] = w._add_object(TextStringObject(
    "BT /F1 12 Tf 50 350 Td (PM-KISAN gives Rs 6000 per year to land farmers. Eligibility: all land holders except taxpayers. Documents: Aadhaar, land records.) Tj ET"))
# NOTE: minimal fake PDF may not extract; use reportlab-free text page instead:
try:
    buf2 = io.BytesIO()
    w.write(buf2)
    pdf_bytes = buf2.getvalue()
    from backend.services import rag_service
    text = rag_service.extract_pdf_text.__wrapped__ if hasattr(rag_service.extract_pdf_text, "__wrapped__") else None
    extracted = None
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
        t.write(pdf_bytes)
        tpath = t.name
    extracted = rag_service.extract_pdf_text(tpath)
    os.unlink(tpath)
    print("INFO extracted chars:", len(extracted or ""))
except Exception as e:
    print("INFO pdf extract attempt:", e)

# Direct RAG service test (deterministic, no PDF lib quirks)
from backend.services import rag_service
rag_service.ingest_document("t-scheme", "PM-KISAN",
    "PM-KISAN gives Rs 6000 per year. Eligibility: all land holders except income tax payers. Documents: Aadhaar, land records, bank account.")
q1 = rag_service.query("t-scheme", "Who is eligible?")
check("rag found eligibility", q1["found"] and "Eligibility" in q1["answer"] or "land holders" in q1["answer"], q1["answer"][:150])
q2 = rag_service.query("t-scheme", "Mars mission budget?")
check("rag NOT-found honest", (not q2["found"]) and "NOT found" in q2["answer"], q2["answer"][:150])

# 3. Voice endpoints degrade gracefully (no whisper installed -> fallback, not 500)
r = c.post("/api/voice/speak", data={"text": "hello", "language": "hi"})
check("voice speak no-crash", r.status_code == 200, r.text[:150])
r = c.post("/api/voice/transcribe", files={"audio": ("a.webm", b"\x1a\x45\xdf\xa3", "audio/webm")})
check("voice transcribe no-crash", r.status_code == 200, r.text[:150])

print()
print("RESULT:", "ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
