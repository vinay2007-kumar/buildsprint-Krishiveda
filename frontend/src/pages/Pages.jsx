import { useState, useEffect, useRef } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { STRINGS } from '../i18n/translations.js'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import VoiceButton from '../components/VoiceButton.jsx'
import { speakText } from '../utils/audio.js'
import { Api } from '../api/client.js'
import { Badge, Card, CardElevated, IconTile, SCHEME_ICONS, SectionTitle, SkeletonBlock, Spinner, useToast } from '../components/ui.jsx'

/* ============================== DASHBOARD — Figma AgroShare inspired ============================== */
export function Dashboard() {
  const { lang, location, geoStatus, setLocation, crop, setCrop } = useApp()
  const navigate = useNavigate()
  const t = STRINGS[lang]
  const [wx, setWx] = useState(null)

  useEffect(() => { Api.weather(location.lat, location.lon, location.name).then(r => setWx(r.data || r)).catch(() => {}) }, [location.lat, location.lon])

  // 12 crops — not only maize
  const CROPS = [
    { id: 1, name: 'wheat', hi: 'गेहूं', gu: 'ઘઉં', icon: '🌾', progress: 80, area: '10' },
    { id: 2, name: 'rice', hi: 'धान', gu: 'ડાંગર', icon: '🌾', progress: 65, area: '8' },
    { id: 3, name: 'maize', hi: 'मक्का', gu: 'મકાઈ', icon: '🌽', progress: 80, area: '10' },
    { id: 4, name: 'cotton', hi: 'कपास', gu: 'કપાસ', icon: '🌿', progress: 45, area: '6' },
    { id: 5, name: 'sugarcane', hi: 'गन्ना', gu: 'શેરડી', icon: '🎋', progress: 70, area: '12' },
    { id: 6, name: 'soybean', hi: 'सोयाबीन', gu: 'સોયાબીન', icon: '🌱', progress: 55, area: '7' },
    { id: 7, name: 'groundnut', hi: 'मूंगफली', gu: 'મગફળી', icon: '🥜', progress: 60, area: '5' },
    { id: 8, name: 'mustard', hi: 'सरसों', gu: 'સરસવ', icon: '🌼', progress: 75, area: '4' },
    { id: 9, name: 'tomato', hi: 'टमाटर', gu: 'ટામેટા', icon: '🍅', progress: 50, area: '3' },
    { id: 10, name: 'potato', hi: 'आलू', gu: 'બટાટા', icon: '🥔', progress: 68, area: '4' },
    { id: 11, name: 'onion', hi: 'प्याज', gu: 'ડુંગળી', icon: '🧅', progress: 52, area: '3' },
    { id: 12, name: 'chilli', hi: 'मिर्च', gu: 'મરચું', icon: '🌶️', progress: 58, area: '2' },
  ]
  const selected = CROPS.find(c => c.name === crop) || CROPS[2]
  const cropLabel = lang === 'hi' ? selected.hi : lang === 'gu' ? selected.gu : selected.name
  const areaLabel = lang === 'hi' ? `${selected.area} हेक्टेयर` : lang === 'gu' ? `${selected.area} હેક્ટર` : `${selected.area} hectares`

  const cards = [
    { to: '/chat', icon: '💬', label: t.ask, sub: t.subAsk, tone: 'farm' },
    { to: '/disease', icon: '🌿', label: t.upload, sub: t.subDetect, tone: 'rose' },
    { to: '/soil', icon: '🧪', label: t.soil, sub: t.subSoil, tone: 'amber' },
    { to: '/weather', icon: '⛅', label: t.weather, sub: t.subWeather, tone: 'sky' },
  ]

  const wxIcon = wx?.current?.condition === 'sunny' ? '☀️' : wx?.current?.condition === 'rainy' ? '🌧️' : '⛅'
  const temp = wx?.current?.temperature != null ? Math.round(wx.current.temperature) : null

  // Human-like time greeting (interfaces-that-feel: warm, time-aware)
  const hour = new Date().getHours()
  const timeWarm = hour < 12 ? (lang === 'hi' ? 'सुप्रभात' : lang === 'gu' ? 'સુપ્રભાત' : 'Good morning') : hour < 17 ? (lang === 'hi' ? 'नमस्ते' : lang === 'gu' ? 'નમસ્તે' : 'Good afternoon') : (lang === 'hi' ? 'शुभ संध्या' : lang === 'gu' ? 'શુભ સાંજ' : 'Good evening')
  const warmMsg = lang === 'hi' ? 'आपकी मेहनत रंग ला रही है — 80% तैयार!' : lang === 'gu' ? 'તમારી મહેનત રંગ લાવી રહી છે!' : "You're doing great — your field is thriving"

  return (
    <div className="space-y-4">
      {/* Greeting — human, warm, time-aware */}
      <div className="px-1 animate-fadeUp">
        <div className="inline-flex items-center gap-2 text-xs font-medium text-farm-700 bg-farm-50 border border-farm-100 rounded-full px-3 py-1">
          <span className="h-1.5 w-1.5 bg-farm-500 rounded-full animate-pulseSoft" /> {timeWarm}
        </div>
        <h1 className="font-bold text-2xl leading-tight text-stone-800 mt-2">{t.dashHi} <span className="inline-block animate-float" style={{ animationDuration: '3s' }}>👋</span></h1>
        <p className="text-sm text-stone-500 mt-1">{t.dashMsg}</p>
        <p className="text-xs text-farm-700 bg-amber-50 border border-amber-100 rounded-full inline-block px-2.5 py-1 mt-2">🌱 {warmMsg}</p>
        {location.name && (
          <button
            onClick={() => {
              const name = prompt(lang === 'hi' ? 'अपना स्थान लिखें:' : 'Enter your location (city name):', location.name)
              if (name && name.trim()) setLocation({ ...location, name: name.trim() })
            }}
            className="flex items-center gap-1.5 mt-3 text-xs text-stone-500 hover:text-farm-700 transition-colors duration-fast"
          >
            <span>📍</span><span className="font-medium">{location.name}</span>
            {geoStatus === 'loading' && <span className="h-2 w-2 bg-amber-400 rounded-full animate-pulse" />}
            {geoStatus === 'denied' && <span className="text-farm-600">(tap to set)</span>}
          </button>
        )}
      </div>

      {/* Crop selector — 12 crops, not only maize */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-bold text-stone-800">{lang === 'hi' ? 'मेरी फसलें' : lang === 'gu' ? 'મારા પાકો' : 'My Crops'} <span className="text-xs font-normal text-stone-500">• {CROPS.length}</span></h3>
          <span className="text-xs text-farm-600 font-medium">{cropLabel} ✓</span>
        </div>
        <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2 -mx-1 px-1">
          {CROPS.map(c => (
            <button key={c.id} onClick={() => setCrop(c.name)} className={`chip shrink-0 transition-all duration-fast ${crop === c.name ? 'active shadow-sm' : 'bg-white hover:border-farm-200'}`}>
              <span>{c.icon}</span> {lang === 'hi' ? c.hi : lang === 'gu' ? c.gu : c.name}
            </button>
          ))}
        </div>
      </div>

      {/* Top grid — plantation (dynamic crop) + weather */}
      <div className="grid gap-3 landscape:grid-cols-5">
        {/* Plantation card — dynamic */}
        <Card className="landscape:col-span-3 p-0 overflow-hidden animate-cardEntrance">
          <div className="p-4 pb-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-stone-800">{selected.icon} {cropLabel}</h3>
              <span className="text-xs bg-farm-50 text-farm-700 px-2.5 py-1 rounded-full font-medium">{selected.progress}% • {t.progressLabel || 'Progress'}</span>
            </div>
          </div>
          <div className="px-4">
            <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-emerald-100 to-amber-50 border border-stone-100 relative h-36">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl">{selected.icon}</div>
                  <div className="text-xs font-bold text-stone-700 mt-1 bg-white/80 backdrop-blur px-3 py-1 rounded-full">{cropLabel} • {areaLabel}</div>
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 h-1.5 bg-stone-200">
                <div className="h-full bg-farm-600 rounded-full transition-all duration-moderate ease-standard" style={{ width: `${selected.progress}%` }} />
              </div>
            </div>
          </div>
          <div className="p-4 space-y-3">
            <div className="flex gap-3">
              <div className="flex-1 bg-amber-50 border border-amber-100 rounded-2xl p-3 hover-lift transition-all duration-base">
                <div className="text-xs text-stone-500">{t.harvestProgress || 'Harvest Progress'}</div>
                <div className="text-sm font-bold text-stone-800 mt-0.5">{selected.progress}%</div>
                <div className="mt-2 h-1.5 bg-white rounded-full overflow-hidden"><div className="h-full bg-farm-600 rounded-full origin-left animate-barGrow" style={{ width: `${selected.progress}%`, animationDelay: '0.2s' }} /></div>
              </div>
              <div className="flex-1 bg-farm-50 border border-farm-100 rounded-2xl p-3 hover-lift transition-all duration-base" style={{ animationDelay: '0.05s' }}>
                <div className="text-xs text-stone-500">{t.harvestIn || 'Harvest in'}</div>
                <div className="text-sm font-bold text-stone-800 mt-0.5">15 {lang === 'hi' ? 'दिन' : lang === 'gu' ? 'દિવસ' : lang === 'bn' ? 'দিন' : lang === 'ta' ? 'நாட்கள்' : lang === 'te' ? 'రోజులు' : 'days'}</div>
                <div className="text-[11px] text-stone-500 mt-1">Dec 10, 2025</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-farm-700 bg-farm-50 border border-farm-100 rounded-2xl px-3 py-2 animate-fadeUp" style={{ animationDelay: '0.3s' }}>
              <span className="text-base">🌱</span>
              <span className="font-medium">{lang === 'hi' ? 'बहुत बढ़िया! बस थोड़ा और — आपकी मेहनत खिल रही है' : lang === 'gu' ? 'સરસ! થોડું બાકી — તમારી મહેનત ખીલી રહી છે' : "You're 80% there — your hard work is blooming"}</span>
            </div>
            <Link to="/disease" className="flex items-center justify-center gap-2 w-full bg-[#ff6d00] hover:bg-[#e65f00] text-white font-semibold rounded-2xl py-3.5 transition-all duration-base ease-standard no-underline shadow-sm hover:shadow-md hover:-translate-y-0.5 pressable will-change-transform">
              <span className="transition-transform duration-fast group-hover:rotate-3">📷</span> {t.upload}
            </Link>
          </div>
        </Card>

        {/* Weather widget — Figma dark green + interfaces-that-feel (soft landing) */}
        <div className="landscape:col-span-2 bg-[#1b4d2e] rounded-3xl p-5 text-white shadow-sm flex flex-col animate-cardEntrance will-change-transform" style={{ animationDelay: '0.08s' }}>
          <div className="flex items-start justify-between">
            <div>
              <div className="text-xs text-white/70 font-medium">{t.weather}</div>
              <div className="text-4xl font-bold mt-1 leading-none transition-all duration-moderate ease-decelerate">{temp != null ? `${temp}°C` : '—°C'}</div>
              <div className="text-sm text-white/80 mt-1 capitalize">{(wx?.current?.description || wx?.current?.condition || '—').replaceAll('_', ' ')}</div>
            </div>
            <div className="h-10 w-10 rounded-2xl bg-white/15 flex items-center justify-center text-2xl animate-float will-change-transform">{wxIcon}</div>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-4">
            <div className="bg-white/10 rounded-2xl px-3 py-2.5">
              <div className="text-[11px] text-white/70">{t.humidity}</div>
              <div className="text-sm font-bold mt-0.5">💧 {wx?.current?.humidity ?? 65}%</div>
            </div>
            <div className="bg-white/10 rounded-2xl px-3 py-2.5">
              <div className="text-[11px] text-white/70">{t.wind}</div>
              <div className="text-sm font-bold mt-0.5">💨 {wx?.current?.wind_speed ?? 12} km/h</div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-white/15">
            <div className="text-xs text-white/70 mb-2">{t.forecastTitle}</div>
            <div className="flex gap-2">
              {(wx?.forecast || [{ date: '2026-09-21', temp_min: 26, temp_max: 30, condition: 'sunny' }, { date: '2026-09-22', temp_min: 24, temp_max: 26, condition: 'rainy' }, { date: '2026-09-23', temp_min: 25, temp_max: 29, condition: 'cloudy' }]).slice(0, 3).map((d, i) => {
                let label = `D${i + 1}`
                try { const dt = new Date(d.date); if (!isNaN(dt)) label = dt.toLocaleDateString(lang === 'hi' ? 'hi-IN' : lang === 'gu' ? 'gu-IN' : 'en-IN', { month: 'short', day: 'numeric' }) } catch {}
                return (
                  <div key={i} className="flex-1 bg-white/10 rounded-2xl py-2 text-center">
                    <div className="text-[11px] text-white/70">{label}</div>
                    <div className="text-lg my-0.5">{d.condition === 'rainy' ? '🌧️' : d.condition === 'sunny' ? '☀️' : '⛅'}</div>
                    <div className="text-xs font-bold">{Math.round(d.temp_min)}° / {Math.round(d.temp_max)}°</div>
                  </div>
                )
              })}
            </div>
            {wx?.is_mock && <div className="text-[10px] text-white/60 mt-2">demo • {t.offline}</div>}
          </div>
        </div>
      </div>

      {/* Quick actions — Figma 4 tiles + motion-system stagger */}
      <div>
        <h3 className="font-bold text-stone-800 mb-3 animate-fadeUp">{t.quick}</h3>
        <div className="grid grid-cols-2 gap-3 landscape:grid-cols-4">
          {cards.map((c, idx) => (
            <Link key={c.to} to={c.to} style={{ animationDelay: `${idx * 45}ms` }} className="bg-white rounded-3xl border border-stone-100 p-4 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-base ease-standard no-underline group will-change-transform animate-cardEntrance">
              <IconTile icon={c.icon} tone={c.tone} />
              <div className="font-bold text-stone-800 mt-3 text-sm leading-snug group-hover:text-farm-700 transition-colors duration-fast">{c.label}</div>
              <div className="text-xs text-stone-500 mt-1 leading-snug">{c.sub}</div>
            </Link>
          ))}
        </div>
        <Link to="/schemes" className="mt-3 bg-white rounded-3xl border border-stone-100 p-4 shadow-sm flex items-center gap-3 no-underline hover:shadow-md transition-shadow">
          <IconTile icon="🏛️" tone="violet" />
          <div className="flex-1 min-w-0">
            <div className="font-bold text-stone-800 text-sm">{t.schemes}</div>
            <div className="text-xs text-stone-500 mt-0.5">{t.subSchemes}</div>
          </div>
          <span className="text-stone-300">›</span>
        </Link>
      </div>

      {/* Alerts — Figma style */}
      <div className="grid gap-3 landscape:grid-cols-2">
        <div className="bg-amber-50 border border-amber-200 rounded-3xl p-4">
          <div className="flex items-start gap-3">
            <div className="h-9 w-9 rounded-2xl bg-amber-100 flex items-center justify-center text-amber-700">⚠️</div>
            <div className="flex-1 min-w-0">
              <div className="font-bold text-stone-800 text-sm">{t.frostRisk || 'Frost risk tomorrow'}</div>
              <div className="text-xs text-stone-600 mt-1 leading-snug">{wx?.agricultural_advice?.[0] || t.frostDesc || 'Cover sensitive crops overnight'}</div>
            </div>
          </div>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-3xl p-4">
          <div className="flex items-start gap-3">
            <div className="h-9 w-9 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700">💧</div>
            <div className="flex-1 min-w-0">
              <div className="font-bold text-stone-800 text-sm">{t.irrigationTitle || 'Irrigation recommended'}</div>
              <div className="text-xs text-stone-600 mt-1 leading-snug">{wx?.agricultural_advice?.[1] || t.irrigationDesc || 'Water early in the morning'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Voice — human, warm (interfaces-that-feel) */}
      <Card className="flex items-center gap-3 py-4 bg-gradient-to-br from-white to-farm-50/50 border-farm-100 hover-lift">
        <div className="h-10 w-10 rounded-2xl bg-farm-600 flex items-center justify-center text-white shadow-sm animate-float will-change-transform" style={{ animationDuration: '4s' }}>🎤</div>
        <div className="flex-1 min-w-0">
          <div className="font-bold text-stone-800 text-sm">{lang === 'hi' ? 'बात करें — दोस्त जैसे' : lang === 'gu' ? 'વાત કરો — મિત્ર જેમ' : 'Talk to me — like a friend'}</div>
          <div className="text-xs text-stone-500">{lang === 'hi' ? 'बस बोलें, मैं सुन रहा हूँ' : lang === 'gu' ? 'બસ બોલો, હું સાંભળું છું' : "Just speak, I'm listening"}</div>
        </div>
        <VoiceButton compact onText={txt => navigate('/chat?q=' + encodeURIComponent(txt))} />
      </Card>
    </div>
  )
}

/* ============================== CHAT — continuous relevant suggestions ============================== */
function getRelevantSuggestions({ lang, crop, lastQ = '', lastA = '', t }) {
  const q = (lastQ + ' ' + lastA).toLowerCase()
  const c = (crop || 'wheat').toLowerCase()
  // Crop-specific pools (localized via t where possible)
  const cropQs = {
    wheat: t.suggestions,
    rice: lang === 'hi' ? ['धान में पानी कितना?', 'राइस ब्लास्ट क्या है?', 'खरपतवार कैसे रोकें?'] : lang === 'gu' ? ['ડાંગરમાં પાણી કેટલું?', 'રાઇસ બ્લાસ્ટ શું?', 'નિંદામણ કેવી રીતે રોકવું?'] : ['How much water for rice?', 'What is rice blast?', 'How to control weeds in rice?'],
    maize: lang === 'hi' ? ['मक्का में खाद कब?', 'मक्का कीट कैसे रोकें?', 'सिंचाई कितनी?'] : lang === 'gu' ? ['મકાઈમાં ખાતર ક્યારે?', 'મકાઈના જીવાત કેવી રીતે રોકવા?', 'સિંચાઈ કેટલી?'] : ['When to fertilize maize?', 'How to control maize pests?', 'How much irrigation for maize?'],
    tomato: lang === 'hi' ? ['टमाटर में कौन सी खाद?', 'टमाटर पत्ती मुरझा रही?', 'टमाटर में पानी?'] : lang === 'gu' ? ['ટામેટામાં કયું ખાતર?', 'ટામેટાના પાન કરમાય છે?', 'ટામેટામાં પાણી?'] : ['What fertilizer for tomato?', 'Tomato leaves wilting?', 'Water for tomato?'],
  }
  // Keyword-based follow-ups
  if (q.includes('yellow') || q.includes('पीला') || q.includes('પીળ') || q.includes('হলুদ') || q.includes('மஞ்சள்')) {
    return lang === 'hi' ? ['कितना यूरिया डालें?', 'पानी रोकें या बढ़ाएं?', 'क्या फंगस है?'] : lang === 'gu' ? ['કેટલું યુરિયા નાખવું?', 'પાણી રોકવું કે વધારવું?', 'શું ફૂગ છે?'] : ['How much urea?', 'Stop or increase water?', 'Is it fungal?']
  }
  if (q.includes('fertiliz') || q.includes('खाद') || q.includes('ખાતર') || q.includes('সার') || q.includes('உரம்')) {
    return lang === 'hi' ? ['मिट्टी pH क्या है?', 'जैविक खाद बताएं', 'कब डालें?'] : lang === 'gu' ? ['માટી pH શું છે?', 'જૈવિક ખાતર કહો', 'ક્યારે નાખવું?'] : ['What is soil pH?', 'Suggest organic fertilizer', 'When to apply?']
  }
  if (q.includes('rain') || q.includes('बारिश') || q.includes('વરસાદ') || q.includes('বৃষ্টি') || q.includes('மழை')) {
    return lang === 'hi' ? ['सिंचाई कब रोकें?', 'जल निकासी कैसे?', 'कटाई कब करें?'] : lang === 'gu' ? ['સિંચાઈ ક્યારે રોકવી?', 'પાણી નિકાલ કેવી રીતે?', 'લણણી ક્યારે?'] : ['When to stop irrigation?', 'How to drain field?', 'When to harvest?']
  }
  if (q.includes('disease') || q.includes('रोग') || q.includes('રોગ') || q.includes('রোগ')) {
    return lang === 'hi' ? ['कौन सी दवा छिड़कें?', 'रोकथाम कैसे?', 'फोटो से जांचें?'] : lang === 'gu' ? ['કઈ દવા છાંટવી?', 'અટકાવ કેવી રીતે?', 'ફોટાથી તપાસો?'] : ['Which spray to use?', 'How to prevent?', 'Check via photo?']
  }
  // Default: crop-specific + generic
  const pool = cropQs[c] || cropQs.wheat
  // Ensure 3, rotate based on lastQ length for variety
  const offset = lastQ.length % Math.max(1, pool.length - 2)
  return pool.slice(offset, offset + 3).length === 3 ? pool.slice(offset, offset + 3) : pool.slice(0, 3)
}

export function ChatAssistant() {
  const { lang, crop, location } = useApp()
  const t = STRINGS[lang]
  const rloc = useLocation()
  const query = new URLSearchParams(rloc.search).get('q') || null
  const [msgs, setMsgs] = useState([{ role: 'assistant', text: t.chatGreet }])
  const [inp, setInp] = useState(query || '')
  const [busy, setBusy] = useState(false)
  const [suggestions, setSuggestions] = useState(t.suggestions)
  const endRef = useRef(null)

  useEffect(() => { setSuggestions(t.suggestions) }, [lang, crop])
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs, busy, suggestions])
  useEffect(() => { if (query) send(query) }, []) // eslint-disable-line

  const send = async (text) => {
    const q = (text ?? inp).trim()
    if (!q || busy) return
    setInp(''); setBusy(true)
    setMsgs(m => [...m, { role: 'user', text: q }, { role: 'assistant', text: '...' }])
    const res = await Api.chat(q, lang, { crop, location: location?.name })
    const answer = res.response || res.data?.response || 'Error'
    setMsgs(m => [...m.slice(0, -1), { role: 'assistant', text: answer }])
    // Update relevant suggestions continuously
    setSuggestions(getRelevantSuggestions({ lang, crop, lastQ: q, lastA: answer, t }))
    try { await speakText(answer, lang) } catch {}
    setBusy(false)
  }

  return (
    <div className="h-[calc(100dvh-13rem)] flex flex-col landscape:h-[calc(100dvh-5.5rem)] bg-[#f1f8ef] landscape:bg-transparent -m-4 p-4 landscape:m-0 landscape:p-0">
      <div className={`flex-1 overflow-y-auto space-y-2.5 pr-1 pb-2 ${msgs.length <= 1 ? 'flex flex-col justify-center' : ''}`}>
        {msgs.map((m, i) => (
          <div key={i} style={{ animationDelay: `${Math.min(i * 60, 300)}ms` }} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-messageSlide will-change-transform`}>
            {m.role === 'assistant' && <div className="h-8 w-8 rounded-full bg-white border border-stone-200 text-center leading-8 text-base shrink-0 mr-2 animate-pop" style={{ animationDelay: `${Math.min(i * 60, 300)}ms` }}>🌾</div>}
            <div className={`max-w-[80%] px-3.5 py-2.5 text-[15px] leading-relaxed transition-all duration-base ease-standard ${m.role === 'user' ? 'bg-farm-600 text-white rounded-3xl rounded-br-lg shadow-sm' : 'bg-white border border-stone-100 shadow-sm rounded-3xl rounded-bl-lg hover:shadow-md'}`}>
              {m.text === '...' ? <span className="inline-flex gap-1 py-1.5"><span className="typing-dot" /><span className="typing-dot" /><span className="typing-dot" /></span> : m.text}
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
      {/* Continuous relevant suggestions */}
      <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2 -mx-1 px-1">
        {suggestions.map(s => <button key={s} onClick={() => send(s)} disabled={busy} className="chip shrink-0 bg-white hover:border-farm-300 hover:text-farm-700 disabled:opacity-50 transition-colors">{s}</button>)}
      </div>
      <div className="flex gap-2 items-end bg-white rounded-3xl border border-stone-200 p-2 shadow-sm">
        <VoiceButton compact variant="secondary" onText={send} />
        <input className="flex-1 bg-transparent px-3 py-2.5 text-base outline-none placeholder:text-stone-400" value={inp} onChange={e => setInp(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} placeholder={t.chatPlaceholder || 'Ask...'} />
        <button onClick={() => send()} disabled={busy || !inp.trim()} className="bg-farm-600 hover:bg-farm-700 text-white h-10 w-10 rounded-2xl flex items-center justify-center disabled:opacity-40 transition-colors">{busy ? <Spinner className="h-5 w-5 text-white" /> : '➤'}</button>
      </div>
    </div>
  )
}

/* ============================== DISEASE ============================== */
export function DiseaseDetection() {
  const { lang } = useApp()
  const t = STRINGS[lang]
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [res, setRes] = useState(null)
  const [busy, setBusy] = useState(false)
  const toast = useToast()
  const onPick = (f) => { setFile(f); setRes(null); setPreview(f ? URL.createObjectURL(f) : null) }
  const go = async () => {
    if (!file || busy) return
    setBusy(true); setRes(null)
    try {
      const r = await Api.disease(file)
      setRes(r)
      if (r.warning) toast(r.warning, 'error')
      else toast('✓ ' + (r.top_prediction?.disease_name?.replaceAll('_', ' ') || 'Done'), 'success')
    } catch { toast(t.offline, 'error') }
    setBusy(false)
  }
  const conf = res?.top_prediction?.confidence || 0
  const confTone = conf >= 0.7 ? 'green' : conf >= 0.6 ? 'amber' : 'red'
  return (
    <div className="space-y-4">
      <Card>
        <SectionTitle>📷 {t.upload}</SectionTitle>
        <label className={`block rounded-3xl border-2 border-dashed transition-colors cursor-pointer ${file ? 'border-farm-400 bg-farm-50' : 'border-stone-300 bg-stone-50 hover:border-farm-400 hover:bg-farm-50'}`}>
          <input type="file" accept="image/*" capture="environment" className="hidden" onChange={e => onPick(e.target.files[0])} />
          {preview ? <div className="p-3"><img src={preview} alt="crop" className="rounded-2xl max-h-64 mx-auto object-contain bg-white" /><div className="text-center text-sm text-stone-600 mt-2">{file?.name}</div></div> : <div className="text-center py-10 px-4"><div className="text-5xl mb-3">📷</div><div className="font-bold text-stone-800">{t.uploadHint}</div><div className="text-xs text-stone-500 mt-1">JPG · PNG · WebP</div></div>}
        </label>
        <button onClick={go} disabled={!file || busy} className="w-full mt-4 bg-[#ff6d00] hover:bg-[#e65f00] disabled:opacity-40 text-white font-semibold rounded-2xl py-3.5 transition-colors flex items-center justify-center gap-2">
          {busy ? <><Spinner className="h-5 w-5 text-white" /> {t.analyzing}</> : `🔍 ${t.checkBtn}`}
        </button>
      </Card>
      {res && (
        <CardElevated>
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0"><div className="text-xs uppercase tracking-widest text-stone-500 font-bold">{t.confidence}</div><h3 className="font-bold text-lg text-stone-800 leading-snug">{res.top_prediction?.disease_name?.replaceAll('_', ' ') || '—'}</h3></div>
            <Badge tone={confTone}>{Math.round(conf * 100)}%</Badge>
          </div>
          {res.model && <div className="text-xs text-stone-400 mt-2">⛏ {t.modelEngine}: {res.model}</div>}
          {res.warning && <div className="mt-3 rounded-2xl bg-danger-50 border border-danger-200 p-3 text-sm text-danger-800">⚠️ {res.warning}</div>}
          {res.symptoms_observed && <div className="mt-3 text-sm text-stone-700"><span className="font-semibold">{t.symptomsLabel}: </span>{res.symptoms_observed}</div>}
          <p className="mt-3 text-[15px] leading-relaxed text-stone-700">{res.ai_analysis}</p>
          <div className="mt-4"><SectionTitle>✅ {t.actionsTitle}</SectionTitle><ul className="space-y-1.5">{(res.recommended_actions || []).map((a, i) => <li key={i} className="flex gap-2 text-sm text-stone-700"><span className="text-success-600 shrink-0 mt-0.5">●</span>{a}</li>)}</ul></div>
          <div className="mt-4"><SectionTitle>🛡️ {t.preventionTitle}</SectionTitle><ul className="space-y-1.5">{(res.preventive_measures || []).map((a, i) => <li key={i} className="flex gap-2 text-sm text-stone-700"><span className="text-farm-600 shrink-0 mt-0.5">●</span>{a}</li>)}</ul></div>
        </CardElevated>
      )}
      {busy && !res && <Card className="space-y-3"><SkeletonBlock className="h-5 w-3/4" /><SkeletonBlock className="h-24" /><SkeletonBlock className="h-24" /></Card>}
    </div>
  )
}

/* ============================== SOIL ============================== */
export function SoilAnalysis() {
  const { lang } = useApp()
  const t = STRINGS[lang]
  const [f, setF] = useState({ crop_id: 1, soil_type: 'black', ph: 7.0, nitrogen: 100, phosphorus: 50, potassium: 50, growth_stage: 'vegetative' })
  const [res, setRes] = useState(null)
  const [busy, setBusy] = useState(false)
  const toast = useToast()
  const set = (k, v) => setF(s => ({ ...s, [k]: v }))
  const go = async () => { setBusy(true); try { setRes(await Api.soil(f)) } catch {} setBusy(false); toast('✓ ' + t.analyzeSoil, 'success') }
  const sliders = [{ k: 'ph', min: 3, max: 10, label: t.phStatus }, { k: 'nitrogen', min: 0, max: 300, label: t.nStatus }, { k: 'phosphorus', min: 0, max: 300, label: t.pStatus }, { k: 'potassium', min: 0, max: 300, label: t.kStatus }]
  return (
    <div className="space-y-4">
      <Card>
        <SectionTitle>🧪 {t.soil}</SectionTitle>
        <div className="space-y-3.5">
          {sliders.map(s => (
            <div key={s.k}>
              <div className="flex justify-between items-center mb-1"><span className="text-sm font-semibold text-stone-700">{s.label}</span><span className="text-sm font-bold text-farm-700 bg-farm-50 rounded-lg px-2 py-0.5">{f[s.k]}{s.k === 'ph' ? '' : ' ppm'}</span></div>
              <input type="range" min={s.min} max={s.max} step="1" value={f[s.k]} onChange={e => set(s.k, Number(e.target.value))} className="w-full accent-farm-600" />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-3 mt-4">
          <div><span className="input-label">{t.soil}</span><div className="flex flex-wrap gap-1.5">{['black', 'red', 'alluvial', 'loamy', 'sandy', 'clay'].map(s => <button key={s} onClick={() => set('soil_type', s)} className={`chip ${f.soil_type === s ? 'active' : 'bg-white'}`}>{s}</button>)}</div></div>
          <div><span className="input-label">Stage</span><div className="flex flex-wrap gap-1.5">{['seedling', 'vegetative', 'flowering', 'fruiting', 'maturity'].map(s => <button key={s} onClick={() => set('growth_stage', s)} className={`chip ${f.growth_stage === s ? 'active' : 'bg-white'}`}>{s}</button>)}</div></div>
        </div>
        <button onClick={go} disabled={busy} className="w-full mt-4 bg-amber-500 hover:bg-amber-600 disabled:opacity-40 text-white font-semibold rounded-2xl py-3.5 transition-colors flex items-center justify-center gap-2">{busy ? <><Spinner className="h-5 w-5 text-white" /> {t.advising}</> : `📋 ${t.analyzeSoil}`}</button>
      </Card>
      {res && (
        <CardElevated>
          <div className="flex items-center gap-4">
            <div className="relative h-24 w-24 shrink-0"><svg viewBox="0 0 100 100" className="h-full w-full -rotate-90"><circle cx="50" cy="50" r="42" fill="none" stroke="#e7e5e4" strokeWidth="12" /><circle cx="50" cy="50" r="42" fill="none" stroke="#1b4d2e" strokeWidth="12" strokeDasharray={`${(res.soil_health_score / 100) * 264} 264`} strokeLinecap="round" /></svg><div className="absolute inset-0 flex flex-col items-center justify-center"><span className="font-bold text-xl text-stone-800">{Math.round(res.soil_health_score)}</span><span className="text-[10px] text-stone-500">{t.healthScore}</span></div></div>
            <div className="flex-1 space-y-2"><div className="flex items-center gap-2"><Badge tone="blue">{t.phStatus}: {res.ph_status}</Badge></div><div className="flex flex-wrap gap-1.5">{['N', 'P', 'K'].map(k => <Badge key={k} tone={res.nutrient_status?.[k] === 'Optimal' ? 'green' : res.nutrient_status?.[k] === 'Medium' ? 'amber' : 'red'}>{k}: {res.nutrient_status?.[k]}</Badge>)}</div></div>
          </div>
          {(res.recommendations || []).length > 0 && <div className="mt-4 space-y-2"><SectionTitle>🌱 {t.actionsTitle}</SectionTitle>{res.recommendations.map((r, i) => <div key={i} className="rounded-2xl bg-farm-50 border border-farm-200 p-3 text-sm"><span className="font-bold text-farm-800">{r.fertilizer_name}</span><span className="text-stone-600"> — {r.dosage_per_acre} kg/acre</span>{r.application_method && <span className="block text-xs text-stone-500 mt-1">{r.application_method}</span>}</div>)}</div>}
          {(res.general_advice || []).length > 0 && <div className="mt-4 text-sm text-stone-600 space-y-1">{(res.general_advice).map((a, i) => <div key={i}>• {a}</div>)}</div>}
        </CardElevated>
      )}
      {busy && !res && <Card className="space-y-3"><SkeletonBlock className="h-24" /><SkeletonBlock className="h-20" /></Card>}
    </div>
  )
}

/* ============================== WEATHER — Figma dark green widget ============================== */
export function WeatherPage() {
  const { location, lang } = useApp()
  const t = STRINGS[lang]
  const [data, setData] = useState(null)
  useEffect(() => { Api.weather(location.lat, location.lon, location.name).then(r => setData(r.data || r)).catch(() => setData(null)) }, [location.lat, location.lon])
  if (!data) return <div className="space-y-3"><Card className="space-y-3"><SkeletonBlock className="h-28" /><SkeletonBlock className="h-12" /></Card><Card className="space-y-2"><SkeletonBlock className="h-4 w-2/3" /><SkeletonBlock className="h-4" /></Card></div>
  const cur = data.current || {}
  const icon = cur.condition === 'rainy' ? '🌧️' : cur.condition === 'sunny' ? '☀️' : cur.condition === 'cloudy' || cur.condition === 'partly_cloudy' ? '⛅' : '🌥️'
  return (
    <div className="space-y-4">
      <div className="bg-[#1b4d2e] rounded-3xl p-6 text-white text-center shadow-sm">
        <div className="text-xs uppercase tracking-widest text-white/70 font-bold">{t.locationLabel}: {location?.name || ''}</div>
        <div className="text-6xl mt-3">{icon}</div>
        <div className="font-bold text-6xl mt-2 leading-none">{Math.round(cur.temperature)}°C</div>
        <div className="text-white/80 mt-2 capitalize">{(cur.description || cur.condition || '').replaceAll('_', ' ')}</div>
        <div className="grid grid-cols-3 gap-2 mt-6">
          {[{ icon: '💧', label: t.humidity, val: `${cur.humidity ?? 0}%` }, { icon: '🌧️', label: t.rainfall, val: `${cur.rainfall ?? 0}mm` }, { icon: '💨', label: t.wind, val: `${cur.wind_speed ?? 0} km/h` }].map((x, i) => (
            <div key={i} className="bg-white/10 rounded-2xl py-3"><div className="text-lg">{x.icon}</div><div className="font-bold text-base leading-tight">{x.val}</div><div className="text-[10px] text-white/70">{x.label}</div></div>
          ))}
        </div>
        {data.is_mock && <div className="text-[11px] text-white/60 mt-3">⚠️ {t.offline}</div>}
      </div>
      <div className="space-y-4 landscape:grid landscape:grid-cols-2 landscape:gap-4 landscape:space-y-0">
        <Card><SectionTitle>🚜 {t.weatherAdvice}</SectionTitle><ul className="space-y-1.5">{(data.agricultural_advice || []).map((a, i) => <li key={i} className="flex gap-2 text-sm text-stone-700"><span className="text-farm-600 shrink-0 mt-0.5">●</span>{a}</li>)}</ul></Card>
        {(data.forecast || []).length > 0 && <Card><SectionTitle>{t.forecastTitle}</SectionTitle><div className="flex gap-2 overflow-x-auto no-scrollbar -mx-1 px-1 pb-1">{(data.forecast || []).slice(0, 5).map((d, i) => {
          let fLabel = d.date
          try { const dt = new Date(d.date); if (!isNaN(dt)) fLabel = dt.toLocaleDateString(lang === 'hi' ? 'hi-IN' : lang === 'gu' ? 'gu-IN' : 'en-IN', { month: 'short', day: 'numeric' }) } catch {}
          return <div key={i} className="shrink-0 w-20 rounded-2xl bg-stone-50 border border-stone-200 p-2.5 text-center"><div className="text-xs text-stone-600 font-medium">{fLabel}</div><div className="text-2xl my-1">{d.condition === 'rainy' ? '🌧️' : d.condition === 'sunny' ? '☀️' : '⛅'}</div><div className="text-sm font-bold text-stone-800">{Math.round(d.temp_min)}–{Math.round(d.temp_max)}°</div><div className="text-[10px] text-farm-600">💧 {Math.round((d.rainfall_probability || 0) * 100)}%</div></div>
        })}</div></Card>}
      </div>
    </div>
  )
}

/* ============================== SCHEMES ============================== */
export function SchemesPage() {
  const { lang } = useApp()
  const t = STRINGS[lang]
  const [schemes, setSchemes] = useState([])
  const [categories, setCategories] = useState({})
  const [activeCat, setActiveCat] = useState('')
  const [expanded, setExpanded] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [showUpload, setShowUpload] = useState(false)
  const [file, setFile] = useState(null)
  const [docId, setDocId] = useState('')
  const [upping, setUpping] = useState(false)
  const [q, setQ] = useState('')
  const [ans, setAns] = useState(null)
  const [asking, setAsking] = useState(false)
  const toast = useToast()
  useEffect(() => { Api.schemeCatalog(activeCat).then(r => { setSchemes(r.data?.schemes || []); setCategories(r.data?.categories || {}) }).catch(() => {}).finally(() => setLoading(false)) }, [activeCat])
  const filtered = schemes.filter(s => !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.tags?.some(tag => tag.includes(search.toLowerCase())))
  const up = async () => { if (!file || upping) return; setUpping(true); try { const r = await Api.schemeUpload(file, file.name); if (r.data?.doc_id) { setDocId(r.data.doc_id); toast(t.schemeUploaded, 'success') } } catch { toast(t.offline, 'error') } setUpping(false) }
  const ask = async () => { if (!docId || !q || asking) return; setAsking(true); try { const r = await Api.schemeQuery(docId, q, lang); setAns(r); if (r.answer) speakText(String(r.answer).slice(0, 250), lang) } catch { toast(t.offline, 'error') } setAsking(false) }
  const catList = Object.entries(categories)
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3"><h2 className="font-bold text-xl text-stone-800">📋 {t.schemes}</h2><button onClick={() => setShowUpload(!showUpload)} className="text-xs text-farm-600 font-medium hover:underline">📄 {showUpload ? 'Hide Upload' : 'Upload PDF'}</button></div>
      {showUpload && (
        <Card className="border-dashed border-2 border-stone-300">
          <SectionTitle>📄 Upload Scheme Document</SectionTitle>
          <label className="block rounded-2xl border-2 border-dashed border-stone-300 bg-stone-50 hover:border-farm-400 hover:bg-farm-50 cursor-pointer"><input type="file" accept=".pdf" className="hidden" onChange={e => setFile(e.target.files[0])} /><div className="text-center py-6 px-4"><div className="text-3xl mb-2">📁</div><div className="font-bold text-stone-800 text-sm">{file ? file.name : 'Drop a scheme PDF here'}</div><div className="text-xs text-stone-500 mt-1">PDF ≤ 10 MB</div></div></label>
          <button onClick={up} disabled={!file || upping} className="w-full mt-3 bg-farm-600 hover:bg-farm-700 disabled:opacity-40 text-white font-semibold rounded-2xl py-3.5 transition-colors flex items-center justify-center gap-2">{upping ? <><Spinner className="h-5 w-5 text-white" /> {t.uploading}</> : `⬆️ ${t.schemeUpload}`}</button>
          {docId && <div className="mt-3 space-y-2"><div className="flex gap-2 items-end"><input value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => e.key === 'Enter' && ask()} placeholder="Ask about this document..." className="input flex-1" /><button onClick={ask} disabled={!q || asking} className="bg-farm-600 hover:bg-farm-700 text-white h-11 px-4 rounded-2xl disabled:opacity-40">{asking ? <Spinner className="h-5 w-5 text-white" /> : '➤'}</button></div>{ans && <div className="bg-farm-50 text-stone-800 rounded-2xl p-4 text-sm leading-relaxed whitespace-pre-wrap">{ans.answer}</div>}</div>}
        </Card>
      )}
      <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1"><button onClick={() => setActiveCat('')} className={`chip shrink-0 ${!activeCat ? 'active' : 'bg-white'}`}>🏷️ All</button>{catList.map(([key, cat]) => <button key={key} onClick={() => setActiveCat(activeCat === key ? '' : key)} className={`chip shrink-0 ${activeCat === key ? 'active' : 'bg-white'}`}>{cat.icon} {cat.label}</button>)}</div>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder={`🔍 Search ${schemes.length} schemes...`} className="input" />
      {loading ? <div className="space-y-3">{[1, 2, 3].map(i => <Card key={i}><SkeletonBlock className="h-24" /></Card>)}</div> : filtered.length === 0 ? <Card><div className="text-center py-8 text-stone-500">No schemes found</div></Card> : (
        <div className="space-y-3">
          {filtered.map((s, idx) => (
            <Card key={s.id} style={{ animationDelay: `${idx * 30}ms` }} className="overflow-hidden p-0 animate-cardEntrance will-change-transform">
              <button onClick={() => setExpanded(expanded === s.id ? null : s.id)} className="w-full text-left flex items-start gap-3 p-5">
                <div className="text-3xl shrink-0 mt-0.5">{SCHEME_ICONS[s.category] || '📋'}</div>
                <div className="min-w-0 flex-1"><h3 className="font-bold text-stone-800 leading-snug">{s.name}</h3><p className="text-sm text-stone-600 mt-1 line-clamp-2">{s.benefit}</p><div className="flex flex-wrap gap-1.5 mt-2">{s.states === 'all_india' && <span className="text-[10px] px-2 py-0.5 bg-farm-50 text-farm-700 rounded-full border border-farm-200">🇮🇳 All India</span>}{s.tags?.slice(0, 3).map(tag => <span key={tag} className="text-[10px] px-2 py-0.5 bg-stone-50 text-stone-600 rounded-full border border-stone-200">{tag}</span>)}</div></div>
                <span className="text-stone-400 text-lg shrink-0">{expanded === s.id ? '▲' : '▼'}</span>
              </button>
              {expanded === s.id && <div className="mx-5 mb-5 pt-4 border-t border-stone-100 space-y-3 animate-fadeUp"><div><div className="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">✅ Eligibility</div><div className="text-sm text-stone-700">{s.eligibility}</div></div><div><div className="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">🎯 Benefits</div><div className="text-sm text-stone-700">{s.benefit}</div></div><div><div className="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">📑 Documents</div><div className="flex flex-wrap gap-1.5 mt-1">{s.documents?.map((doc, i) => <span key={i} className="text-xs px-2 py-1 bg-stone-50 text-stone-700 rounded-lg border border-stone-200">• {doc}</span>)}</div></div><div><div className="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">📝 How to Apply</div><div className="text-sm text-stone-700">{s.how_to_apply}</div></div><div className="flex flex-wrap gap-3 pt-2">{s.website && <a href={s.website} target="_blank" rel="noopener" className="text-xs text-farm-600 font-medium hover:underline">🌐 Official Website</a>}{s.helpline && <span className="text-xs text-stone-500">📞 Helpline: {s.helpline}</span>}</div></div>}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
