// Push-to-talk mic (Web Speech API STT) + ElevenLabs-first TTS on result.
import { useState } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { speakText, stopSpeak } from '../utils/audio.js'
import { Spinner } from './ui.jsx'

export default function VoiceButton({ onText, variant = 'primary', compact = false }) {
  const { lang } = useApp()
  const [listening, setListening] = useState(false)
  const [speaking, setSpeaking] = useState(false)

  const listen = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Voice input not supported in this browser. Please type.') ; return }
    const r = new SR()
    r.lang = lang === 'hi' ? 'hi-IN' : lang === 'gu' ? 'gu-IN' : 'en-IN'
    r.interimResults = false
    r.maxAlternatives = 1
    r.onstart = () => { setListening(true); stopSpeak() }
    r.onend = () => setListening(false)
    r.onresult = async (e) => {
      const transcript = (e.results[0]?.[0]?.transcript || '').trim()
      if (!transcript) return
      if (onText) {
        setSpeaking(true)
        try { await onText(transcript) } finally { setSpeaking(false) }
      }
    }
    r.onerror = () => setListening(false)
    r.start()
  }

  const cls = compact
    ? 'h-12 w-12 shrink-0 rounded-2xl flex items-center justify-center text-xl transition-all duration-base ease-standard active:scale-95 shadow-sm hover:shadow-md will-change-transform pressable'
    : 'btn w-full transition-all duration-base ease-standard pressable'
  const tone = listening
    ? 'bg-danger-500 text-white shadow-md animate-pulseSoft'
    : speaking
      ? 'bg-farm-700 text-white shadow-sm opacity-85'
      : variant === 'secondary'
        ? 'bg-farm-50 text-farm-700 hover:bg-farm-100 border border-farm-200'
        : 'bg-farm-600 text-white hover:bg-farm-700 shadow-sm hover:shadow-md'

  return (
    <span className="relative inline-flex">
      {listening && <span className="absolute inset-0 rounded-2xl bg-danger-400 animate-pulseRing pointer-events-none" aria-hidden="true" />}
      <button onClick={listen} className={`${cls} ${tone} relative`} aria-label="Voice input">
        {listening
          ? compact ? <span className="relative flex h-3 w-3"><span className="animate-pulseRing absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span></span> : <><span className="h-2 w-2 bg-white rounded-full animate-pulse" /> <span>🎙️ {lang === 'gu' ? 'સાંભળી રહ્યા...' : lang === 'hi' ? 'सुन रहे हैं...' : 'Listening...'}</span></>
          : speaking
            ? <Spinner className="h-5 w-5" />
            : compact ? <span className="transition-transform duration-fast group-hover:scale-110">🎤</span> : <><span>🎙️</span><span>{lang === 'gu' ? 'બોલો' : lang === 'hi' ? 'बोलें' : 'Speak'}</span></>
        }
      </button>
    </span>
  )
}

export { speakText, stopSpeak }