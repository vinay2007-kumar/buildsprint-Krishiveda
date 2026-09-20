"""Debug HF search: with/without auth + filter to find plant disease models."""
import asyncio, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings

async def main():
    async with httpx.AsyncClient(timeout=30.0) as c:
        # 1) raw count without filter
        r = await c.get("https://huggingface.co/api/models", params={"search": "plant disease"})
        print("no-filter status:", r.status_code, "items:", len(r.json()) if r.status_code == 200 else r.text[:100])
        if r.status_code == 200:
            for m in r.json()[:10]:
                print("   ", m.get("id"), "| gated:", m.get("gated"), "| pipeline:", m.get("pipeline_tag"),
                      "| dl:", m.get("downloads"), "| tags:", [t for t in m.get("tags", []) if "classification" in t or "vit" in t][:3])
        # 2) with auth
        r2 = await c.get("https://huggingface.co/api/models",
                         params={"search": "plant disease", "limit": 20},
                         headers={"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"})
        print("auth status:", r2.status_code, "items:", len(r2.json()) if r2.status_code == 200 else r2.text[:100])
        # 3) by model id lookups of well-known repos (public metadata only)
        for mid in ["nateraw/vit-base-beans", "AR0000/CropDisease_VisionTransformer"]:
            r3 = await c.get(f"https://huggingface.co/api/models/{mid}",
                             headers={"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"})
            j = r3.json() if r3.status_code == 200 else {}
            print(f"lookup {mid}:", r3.status_code, "| gated:", j.get("gated"), "| pipeline:", j.get("pipeline_tag"),
                  "| private:", j.get("private"), "| dl:", j.get("downloads"))

asyncio.run(main())