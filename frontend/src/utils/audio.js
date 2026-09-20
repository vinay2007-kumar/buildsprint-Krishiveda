// Audio helpers — ElevenLabs-first TTS with graceful browser fallback.
import { Api } from '../api/client.js'

let audioEl = null
function getAudio() {
  if (!audioEl) { audioEl = new Audio(); audioEl.preload = 'auto' }
  return audioEl
}

// Try backend TTS (ElevenLabs → edge-tts → gTTS). On any failure, browser speechSynthesis.
export async function speakText(text, lang = 'hi') {
  if (!text) return 'browser'
  try {
    const res = await Api.speak(text, lang) // { audio_url, source } or fallback
    const url = res.audio_url || res.data?.audio_url
    if (url) {
      await new Promise((resolve, reject) => {
        const a = getAudio()
        a.onended = resolve
        a.onerror = reject
        a.src = url
        a.play().catch(reject)
      })
      return res.source || 'backend'
    }
  } catch (e) { /* fall through to browser */ }
  return browserSpeak(text, lang)
}

export function browserSpeak(text, lang = 'hi') {
  try {
    speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text.slice(0, 300))
    u.lang = lang === 'hi' ? 'hi-IN' : lang === 'gu' ? 'gu-IN' : 'en-IN'
    speechSynthesis.speak(u)
    return 'browser'
  } catch { return 'none' }
}

export function stopSpeak() {
  try { speechSynthesis.cancel() } catch {}
  if (audioEl) { try { audioEl.pause() } catch {} }
}