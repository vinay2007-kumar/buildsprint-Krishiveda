"""Check candidate pre-trained PlantVillage disease models on HF (gating, task, usage)."""
import asyncio, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings

# Pre-trained models fine-tuned on PlantVillage (38 classes) / crop disease datasets
CANDIDATES = [
    "AR0000/CropDisease_VisionTransformer",
    "matthewppeters/Crop_Identification_and_Disease_Detection",
    "chandraprakash/PlantVillage",
    "gunjan30/Plant-disease",
    "nateraw/vit-base-beans",
    "sachinkalsi/plant-disease-detection",
    "samiullahsaleem/Improving-Crop-Classification",
]

async def main():
    async with httpx.AsyncClient(timeout=30.0) as c:
        for mid in CANDIDATES:
            try:
                r = await c.get(f"https://huggingface.co/api/models/{mid}")
                if r.status_code != 200:
                    print(f"{r.status_code}  {mid}  (no metadata)")
                    continue
                j = r.json()
                print(f"OK  {mid}")
                print(f"    gated={j.get('gated')}  pipeline={j.get('pipeline_tag')}  library={j.get('library_name')}  downloads={j.get('downloads')}")
                tags = j.get("tags", [])
                print(f"    tags={[t for t in tags if t.startswith(('model_type','architectures','google/vit','microsoft/'))][:5]}")
            except Exception as e:
                print(f"ERR {mid}: {e}")

asyncio.run(main())