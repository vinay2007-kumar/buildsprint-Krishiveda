import axios from 'axios'

// Backend base: same origin in prod, localhost:8000 in dev (vite proxy handles /api)
const api = axios.create({ baseURL: '', timeout: 60000 })

async function safe(promise, fallback) {
  try { const r = await promise; return r.data }
  catch (e) { console.warn('API offline, mock fallback', e?.message); return fallback }
}

export const Api = {
  chat: (message, language = 'hi', context = {}) =>
    safe(api.post('/api/chat', { message, language, context }),
      { response: mockChat(message, language), language, session_id: 'demo', confidence: 0.4 }),
  disease: (file, crop = '') => {
    const fd = new FormData(); fd.append('image', file); if (crop) fd.append('crop', crop)
    return safe(api.post('/api/disease/predict', fd),
      { top_prediction: { disease_name: 'Tomato_Early_blight', confidence: 0.72 },
        predictions: [], ai_analysis: 'Demo result (backend offline).', recommended_actions: ['Consult expert.'],
        preventive_measures: ['Crop rotation.'], warning: 'Backend offline - demo data.' })
  },
  soil: (payload) =>
    safe(api.post('/api/soil/analyze', payload),
      { soil_health_score: 62, nutrient_status: { N: 'Low', P: 'Medium', K: 'Optimal' },
        ph_status: 'Neutral', recommendations: [{ fertilizer_name: 'Urea (demo)', dosage_per_acre: 30 }],
        soil_amendments: [], general_advice: ['Backend offline - demo data.'] }),
  weather: (lat = 23.03, lon = 72.58, location = '') =>
    safe(api.get('/api/weather', { params: { lat, lon, location } }),
      { success: true, data: { current: { temperature: 31, humidity: 60, condition: 'partly_cloudy' }, forecast: [], agricultural_advice: ['Backend offline.'] } }),
  schemeUpload: (file, title) => {
    const fd = new FormData(); fd.append('file', file); fd.append('title', title)
    return safe(api.post('/api/scheme/upload', fd), { success: true, data: { doc_id: 'demo', chunks: 5 } })
  },
  schemeQuery: (document_id, question, language = 'hi') =>
    safe(api.post('/api/scheme/query', { document_id, question, language }),
      { answer: 'Backend offline - upload + query needs server.', source_chunks: [], confidence: 0 }),
  schemeList: () => safe(api.get('/api/scheme/list'), { success: true, data: [] }),
  schemeCatalog: (category = '') => safe(api.get('/api/scheme/catalog', { params: category ? { category } : {} }),
    { success: true, data: { schemes: [], categories: {}, total: 0 } }),
  // Voice: ElevenLabs-first on backend, degrades to browser (utils/audio.js)
  speak: (text, language = 'hi') => {
    const fd = new FormData(); fd.append('text', text); fd.append('language', language)
    return safe(api.post('/api/voice/speak', fd),
      { audio_url: '', source: 'browser-tts', message: 'Server TTS unavailable.' })
  },
  transcribe: (file, language = 'hi') => {
    const fd = new FormData(); fd.append('audio', file); if (language) fd.append('language', language)
    return safe(api.post('/api/voice/transcribe', fd),
      { success: true, data: { transcript: '', source: 'unavailable' } })
  },
}

function mockChat(msg, lang) {
  if (lang === 'hi') return 'नमस्ते! मैं KrishiVeda हूं। (डेमो मोड - सर्वर बंद है) अपना सवाल फसल + मिट्टी के साथ पूछें।'
  if (lang === 'gu') return 'નમસ્તે! હું KrishiVeda છું. (ડેમો મોડ) પાક + માટી સાથે પ્રશ્ન પૂછો.'
  return 'Hello! I am KrishiVeda. (Demo mode - server offline) Ask with crop + soil details.'
}

export default api
