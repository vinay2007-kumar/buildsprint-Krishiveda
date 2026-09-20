"""Test serverless HF inference on top public plant-disease models with a realistic spotted leaf."""
import asyncio, io, sys
sys.path.insert(0, r"C:\Users\vinay\OneDrive\Documents\Default Project\KrishiVeda")
import httpx
from backend.config import settings
from PIL import Image, ImageDraw

# Build a leaf-like image (green with brown spots → plausibly diseased)
img = Image.new("RGB", (256, 256), (34, 130, 34))
d = ImageDraw.Draw(img)
for _ in range(60):
    x, y = __import__("random").randint(10, 245), __import__("random").randint(10, 245)
    r, g = __import__("random").randint(80, 150), __import__("random").randint(60, 110)
    d.ellipse([x, y, x + __import__("random").randint(6, 22), y + __import__("random").randint(6, 22)], fill=(r, g, 30))
buf = io.BytesIO(); img.save(buf, format="JPEG")
LEAF = buf.getvalue()

MODELS = [
    "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification",
    "gianlab/swin-tiny-patch4-window7-224-finetuned-plantdisease",
    "nateraw/vit-base-beans",
]

async def test(model):
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    try:
        async with httpx.AsyncClient(timeout=90.0) as c:
            r = await c.post(url, headers={
                "Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}",
                "Content-Type": "image/jpeg",
            }, content=LEAF)
        if r.status_code == 200:
            data = r.json()
            top = data[:3] if isinstance(data, list) else data
            print(f"INFER 200  {model}")
            for t in top:
                if isinstance(t, dict):
                    print(f"    {t.get('label')}  {t.get('score'):.3f}")
            return True
        print(f"INFER {r.status_code}  {model}  :: {r.text[:160]}")
    except Exception as e:
        print(f"INFER ERR {model}  :: {e}")
    return False

async def main():
    for m in MODELS:
        if await test(m):
            print("\nFIRST WORKING PLANT-DISEASE MODEL:", m)
            break

asyncio.run(main())