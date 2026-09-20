"""Image validation + storage helpers."""

import os
from backend.config import settings


def validate_image(data: bytes) -> tuple:
    """Check bytes are a real image (PIL) and reasonable size."""
    if not data or len(data) < 100:
        return False, "Empty file."
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = img.size
        if w < 50 or h < 50:
            return False, "Image too small. Upload a clear close-up leaf photo."
        return True, "ok"
    except Exception as e:
        return False, f"Not a valid image ({e}). Upload JPG/PNG."


def save_upload(data: bytes, filename: str, subdir: str = "images") -> str:
    """Save upload, return public URL path."""
    d = os.path.join(settings.UPLOAD_DIR, subdir)
    os.makedirs(d, exist_ok=True)
    # Sanitize filename
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)[-80:]
    path = os.path.join(d, safe)
    with open(path, "wb") as f:
        f.write(data)
    return f"/uploads/{subdir}/{safe}"
