// UI primitives — Figma-inspired (AgroShare / Positivus) + designer-skills
import { createContext, useCallback, useContext, useState } from 'react'
import { Link } from 'react-router-dom'

/* ---- Toasts ---- */
const ToastCtx = createContext(() => {})
export const useToast = () => useContext(ToastCtx)
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const push = useCallback((message, kind = 'info') => {
    const id = Math.random().toString(36).slice(2)
    setToasts(t => [...t, { id, message, kind }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3500)
  }, [])
  const tones = { success: 'bg-success-50 text-success-800 border-success-200', error: 'bg-danger-50 text-danger-800 border-danger-200', info: 'bg-farm-50 text-farm-800 border-farm-200' }
  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="fixed top-16 inset-x-0 flex flex-col items-center gap-2 px-4 z-50 pointer-events-none">
        {toasts.map(t => (
          <div key={t.id} className={`px-4 py-3 rounded-2xl border shadow-lg animate-pop max-w-md text-sm font-medium ${tones[t.kind] || tones.info}`}>{t.message}</div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

/* ---- Spinner / skeleton ---- */
export function Spinner({ className = 'h-5 w-5 text-white' }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  )
}
export function SkeletonBlock({ className = 'h-4' }) { return <div className={`skeleton ${className}`} aria-hidden="true" /> }

/* ---- Badge ---- */
const badgeTones = { green: 'bg-success-50 text-success-700 border border-success-200', amber: 'bg-warn-50 text-warn-700 border border-warn-200', red: 'bg-danger-50 text-danger-700 border border-danger-200', blue: 'bg-info-50 text-info-700 border border-info-200', neutral: 'bg-stone-100 text-stone-700 border border-stone-200', farm: 'bg-farm-50 text-farm-700 border border-farm-200' }
export function Badge({ children, tone = 'neutral', className = '' }) {
  return <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${badgeTones[tone]} ${className}`}>{children}</span>
}

/* ---- Card — Figma style: white, rounded-2xl, soft shadow + motion-system ---- */
export function Card({ children, className = '', onClick, as: Tag = 'div' }) {
  const pressable = onClick ? 'hover-lift pressable cursor-pointer will-change-transform' : 'hover-lift will-change-transform'
  return <Tag onClick={onClick} className={`bg-white rounded-3xl shadow-sm border border-stone-100 p-5 animate-cardEntrance ${pressable} ${className}`}>{children}</Tag>
}
export function CardElevated({ children, className = '', onClick }) {
  const pressable = onClick ? 'hover-lift-lg pressable cursor-pointer will-change-transform' : 'hover-lift will-change-transform'
  return <div className={`bg-white rounded-3xl shadow-md border border-stone-100 p-5 animate-cardEntrance ${pressable} ${className}`} onClick={onClick}>{children}</div>
}

/* ---- Icon tile — Figma: light mint bg, green icon + micro-interaction ---- */
const tileTones = {
  farm: 'bg-farm-50 text-farm-700',
  sky: 'bg-sky-50 text-sky-700',
  amber: 'bg-amber-50 text-amber-700',
  violet: 'bg-violet-50 text-violet-700',
  rose: 'bg-rose-50 text-rose-700',
}
export function IconTile({ icon, tone = 'farm', className = 'h-11 w-11 text-xl rounded-2xl' }) {
  return <div className={`flex items-center justify-center ${tileTones[tone]} ${className} transition-transform duration-fast ease-standard group-hover:scale-105`}><span aria-hidden="true" className="transition-transform duration-fast">{icon}</span></div>
}

/* ---- Section title — Figma: small semibold, stone-700 ---- */
export function SectionTitle({ children, className = '' }) {
  return <h2 className={`text-sm font-bold text-stone-800 mb-3 ${className}`}>{children}</h2>
}

export const SCHEME_ICONS = {
  income_support: '💰', insurance: '🛡️', credit: '🏦', irrigation: '💧',
  market: '🏪', price_support: '📊', infrastructure: '🏗️', production: '🌾',
  mechanization: '🚜', organic: '🌿', soil_health: '🧪', storage: '🏭',
  oilseeds: '🌻', horticulture: '🎋', processing: '📦', collective: '🤝',
}
