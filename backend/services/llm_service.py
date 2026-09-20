"""
LLM service via HuggingFace Inference API with rule-based fallback.

- Primary: HuggingFace Inference API (no local GPU needed, hackathon-friendly).
- Fallback: deterministic agricultural rule-based answers when token/API missing.
- Keeps responses short, farmer-friendly, in en/hi/gu.
"""

import structlog
from typing import Optional

from backend.config import settings

logger = structlog.get_logger()

SYSTEM_PROMPT = (
    "You are KrishiVeda, a helpful farming assistant for smallholder farmers in India. "
    "Rules: short simple sentences, no jargon, practical steps only, "
    "mention approximate quantities in kg/acre, warn that advice is guidance not guarantee, "
    "ask to consult local extension officer for severe cases."
)

LANG_INSTRUCTION = {
    "en": "Reply in simple English.",
    "hi": "सरल हिंदी में जवाब दें। किसान के लिए आसान भाषा।",
    "gu": "સરળ ગુજરાતીમાં જવાબ આપો. ખેડૂત માટે સરળ ભાષા.",
}


async def generate_response(prompt: str, language: str = "hi", max_tokens: int = 400) -> dict:
    """Generate LLM response. Returns {text, source, confidence}."""
    lang = language if language in ("en", "hi", "gu") else "hi"
    full_prompt = f"{SYSTEM_PROMPT}\n{LANG_INSTRUCTION[lang]}\nFarmer question: {prompt}\nAnswer:"

    # Try HuggingFace API if token configured.
    # Primary: OpenAI-compatible chat completions router. Fallback: legacy text-gen.
    token = getattr(settings, "HUGGINGFACE_TOKEN", None)
    model = getattr(settings, "LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    if token:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    "https://router.huggingface.co/v1/chat/completions",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"model": model,
                          "messages": [{"role": "system", "content": f"{SYSTEM_PROMPT} {LANG_INSTRUCTION[lang]}"},
                                       {"role": "user", "content": prompt}],
                          "max_tokens": max_tokens, "temperature": 0.6},
                )
                if r.status_code == 200:
                    text = r.json()["choices"][0]["message"]["content"].strip()
                    if text:
                        return {"text": text[:2000], "source": "huggingface", "confidence": 0.85}
                else:
                    logger.warning("HF chat API non-200", status=r.status_code, body=r.text[:200])
        except Exception as e:
            logger.warning("HF API failed, using fallback", error=str(e))

    # Rule-based fallback (works offline, good for demo)
    return {"text": fallback_answer(prompt, lang), "source": "rule-based-fallback", "confidence": 0.55}


def fallback_answer(prompt: str, lang: str) -> str:
    """Keyword-based agricultural answers for offline demo."""
    p = prompt.lower()
    if any(k in p for k in ["yellow", "पीला", "પીળ", "leaf"]):
        if lang == "hi":
            return ("पीले पत्ते अक्सर नाइट्रोजन की कमी या पानी की समस्या से होते हैं। "
                    "1) खेत में पानी जमा न होने दें। 2) यूरिया 25-30 kg/एकड़ टॉप-ड्रेसिंग करें (मिट्टी जांच के बाद)। "
                    "3) 7 दिन में सुधार न हो तो कृषि अधिकारी से संपर्क करें। यह सलाह मार्गदर्शन है, गारंटी नहीं।")
        if lang == "gu":
            return ("પીળા પાંદડા ઘણીવાર નાઇટ્રોજનની ઉણપ કે પાણીની સમસ્યાથી થાય છે. "
                    "1) ખેતરમાં પાણી ભરાવા ન દો. 2) માટી તપાસ પછી યુરિયા 25-30 kg/એકર આપો. "
                    "3) 7 દિવસમાં સુધારો ન થાય તો કૃષિ અધિકારીનો સંપર્ક કરો.")
        return ("Yellow leaves are often nitrogen deficiency or waterlogging. "
                "1) Drain excess water. 2) After soil test, top-dress urea 25-30 kg/acre. "
                "3) If no improvement in 7 days, consult extension officer. Guidance only, not guaranteed.")
    if any(k in p for k in ["irrigat", "सिंचाई", "પિયત", "पानी"]):
        if lang == "hi":
            return ("सिंचाई सुबह 6-9 बजे करें। भारी बारिश के बाद 2-3 दिन रुकें। "
                    "मिट्टी में 3-4 cm गहराई तक नमी जांचें — सूखी हो तभी पानी दें।")
        if lang == "gu":
            return ("સિંચાઈ સવારે 6-9 વાગ્યે કરો. ભારે વરસાદ પછી 2-3 દિવસ રાહ જુઓ. "
                    "માટીમાં 3-4 cm ઊંડે ભેજ તપાસો — સૂકી હોય ત્યારે જ પાણી આપો.")
        return ("Irrigate early morning 6-9 AM. Wait 2-3 days after heavy rain. "
                "Check moisture 3-4 cm deep — water only if dry.")
    if any(k in p for k in ["fertiliz", "खाद", "उर्वरक", "ખાતર"]):
        if lang == "hi":
            return ("सामान्य सलाह: मिट्टी जांच के बिना भारी खाद न डालें। "
                    "गेहूं के लिए बुवाई पर DAP 50 kg/एकड़ + यूरिया 30 kg/एकड़ आम है। "
                    "सही मात्रा मिट्टी NPK पर निर्भर है — Soil Analysis मॉड्यूल में मान डालें।")
        if lang == "gu":
            return ("સામાન્ય સલાહ: માટી તપાસ વિના ભારે ખાતર ન નાખો. "
                    "ઘઉં માટે વાવણી સમયે DAP 50 kg/એકર + યુરિયા 30 kg/એકર સામાન્ય છે. "
                    "ચોક્કસ માત્રા માટે Soil Analysis માં મૂલ્યો નાખો.")
        return ("General advice: avoid heavy fertilizer without soil test. "
                "For wheat, basal DAP 50 kg/acre + urea 30 kg/acre is common. "
                "Enter your NPK values in Soil Analysis for exact dose.")
    if lang == "hi":
        return ("आपका सवाल मिल गया। संक्षिप्त सलाह: फसल, मिट्टी और मौसम की जानकारी दें तो बेहतर उत्तर मिलेगा। "
                "गंभीर रोग/कीट में स्थानीय कृषि अधिकारी से जांच कराएं। यह AI सलाह मार्गदर्शन है।")
    if lang == "gu":
        return ("તમારો પ્રશ્ન મળ્યો. સારી સલાહ માટે પાક, માટી અને હવામાનની માહિતી આપો. "
                "ગંભીર રોગ/જીવાતમાં સ્થાનિક કૃષિ અધિકારી પાસે તપાસ કરાવો. આ AI સલાહ માર્ગદર્શન છે.")
    return ("Got your question. For better advice share crop, soil and weather details. "
            "For severe pest/disease, get field inspection by extension officer. AI guidance only.")
