"""Language detection + UI language helpers (en/hi/gu)."""

import re

SUPPORTED = ("en", "hi", "gu")


def normalize_lang(code: str | None) -> str:
    c = (code or "hi").lower()
    if c.startswith("hi"): return "hi"
    if c.startswith("gu"): return "gu"
    if c.startswith("en"): return "en"
    return "hi"


def detect_language(text: str) -> str:
    """Naive script-based detection: Devanagari -> hi, Gujarati -> gu, else en."""
    if not text:
        return "hi"
    if re.search(r"[\u0A80-\u0AFF]", text):
        return "gu"
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    return "en"
