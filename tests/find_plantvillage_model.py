"""Search HF hub for UNGATED plant disease / crop classification models, then test serverless inference."""
import asyncio, io, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings
from PIL import Image

async def search(query):
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.get("https://huggingface.co/api/models",
                        params={"search": query, "limit": 40, "filter": "pipeline_tag:image-classification"})
        if r.status_code != 200:
            print(f"search '{query}' HTTP {r.status_code}")
            return []
        out = []
        for m in r.json():
            gated = m.get("gated") not in (None, False)
            # include only public + not gated + has downloads
            if not gated and (m.get("downloads") or 0) > 0:
                out.append((m["id"], m.get("downloads"), m.get("tags", [])[:3]))
        return out

async def test_inference(model):
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    img = Image.new("RGB", (224, 224), (80, 140, 60))
    buf = io.BytesIO(); img.save(buf, format="JPEG")
    try:
        async with httpx.AsyncClient(timeout=60.0) as c:
            r = await c.post(url, headers={
                "Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}",
                "Content-Type": "image/jpeg",
            }, content=buf.getvalue())
        body = r.text[:200].replace("\n", " ")
        print(f"  INFER {r.status_code}  {model}  :: {body}")
        return r.status_code == 200
    except Exception as e:
        print(f"  INFER ERR {model}: {e}")
        return False

async def main():
    all_found = []
    for q in ("plantvillage", "plant disease", "crop disease", "plant-disease classification"):
        found = await search(q)
        print(f"== search '{q}': {len(found)} ungated image-classification models")
        for mid, dl, _ in found:
            print(f"   {mid}  (downloads={dl})")
        all_found.extend(found)
    # Dedupe, keep top 10 by downloads
    seen, top = set(), []
    for mid, dl, _ in sorted(all_found, key=lambda x: -x[1]):
        if mid not in seen:
            seen.add(mid); top.append(mid)
    print("\n== TOP CANDIDATES BY DOWNLOADS (ungated):")
    for mid in top[:10]:
        print("  *", mid)
    print("\n== TESTING SERVERLESS INFERENCE (first 5):")
    for mid in top[:5]:
        if await test_inference(mid):
            print("FIRST WORKING SERVERLESS MODEL:", mid)
            break

asyncio.run(main())