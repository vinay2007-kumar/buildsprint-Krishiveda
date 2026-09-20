# KrishiVeda 🌾 - AI Agricultural Assistant

Voice-first assistant for smallholder farmers. Hindi, Gujarati, English.

## Modules
- 📷 Crop disease detection - REAL pre-trained PlantVillage MobileNetV2 (serverless HF inference, no training) + auto mock fallback
- 💬 AI chatbot (HuggingFace Inference Providers - Llama-3.1-8B, offline fallback)
- 🧪 Soil & fertilizer recommendations (rule-based NPK engine)
- 🌦️ Weather + irrigation advice (Open-Meteo, no key)
- 🏛️ Government scheme RAG (PDF → chunks → answer with citations)
- 🎤 Voice (ElevenLabs TTS/STT primary → edge-tts/gTTS → browser Web Speech fallback)

## Design system (designer-skills)
UI rebuilt from the [Designer Skills Pack](../designer-skills) (design-token, color-system,
typography-scale, feedback-patterns, loading-states):
- Token layer in `frontend/tailwind.config.js` — full farm-green tonal scale, semantic colors,
  modular type scale, spacing, elevation, motion tokens
- Component layer — `index.css` (.card/.btn/.chip/.nav-item/.skeleton…) + `components/ui.jsx`
  (Card, Badge, IconTile, Spinner, Skeleton, toast feedback system)
- Mobile-first shell with branded header, language pill, 5-tab bottom nav with active states
- All 6 pages rebuilt: greeting hero + quick-action grid, chat with typing indicator + suggestion
  chips, disease dropzone + confidence result card, soil sliders + health gauge, weather hero +
  forecast chips, schemes flow with toast feedback
- Reduce-motion, AA-contrast color pairs, focus-visible rings, safe-area nav padding

## Voice: ElevenLabs
Set in `.env` (free at https://elevenlabs.io/api-keys):
```
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # ee Rachel; swap for a Hindi voice (e.g. Kriya)
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```
TTS chain: ElevenLabs → edge-tts → gTTS → browser speechSynthesis (never crashes).
STT chain: ElevenLabs scribe_v1 → faster-whisper → browser Web Speech (frontend default mic).

## Quick Start

### Backend
```bash
cd KrishiVeda
copy .env.example .env
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```
Docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173 (proxies /api to :8000)

### Demo without backend
Frontend works offline with mock data - perfect for UI demo.

## API
- POST /api/disease/predict (image)
- POST /api/chat
- POST /api/soil/analyze
- GET /api/weather?lat=23.03&lon=72.58
- POST /api/scheme/upload (PDF)
- POST /api/scheme/query
- POST /api/voice/transcribe, POST /api/voice/speak

## Safety
- Confidence scores + low-confidence warnings on all predictions.
- Uncertain image results are NEVER presented as confirmed diagnosis - expert consult advised.
- Scheme answers cite uploaded PDF; missing info explicitly marked NOT FOUND.
- Advice labeled guidance, not guaranteed. Severe cases → extension officer.

## Disease model: pre-trained, no training needed
Uses PlantVillage-trained MobileNetV2 via HuggingFace serverless inference (your token). Config in `.env`:
- `DISEASE_MODEL=` - swap any supported image-classification model
- `USE_REAL_DISEASE_MODEL=false` - force offline deterministic mock (never crashes)
