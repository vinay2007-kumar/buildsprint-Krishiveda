import { Link, useLocation } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'
import { STRINGS, LANGS } from '../i18n/translations.js'

const NAV = [
  { to: '/', icon: '🏠', key: 'navHome', label: 'Dashboard' },
  { to: '/chat', icon: '💬', key: 'navAsk', label: 'Ask AI' },
  { to: '/disease', icon: '📷', key: 'navUpload', label: 'Scan Plant' },
  { to: '/weather', icon: '🌦️', key: 'navWeather', label: 'Weather' },
  { to: '/schemes', icon: '🏛️', key: 'navSchemes', label: 'Schemes' },
]

export default function Layout({ children }) {
  const { lang, setLang } = useApp()
  const t = STRINGS[lang]
  const loc = useLocation()

  return (
    <div className="min-h-screen bg-[#f1f8ef] landscape:bg-[#eef5eb]">
      {/* Header — Figma-inspired: white, soft border, green brand + motion-system */}
      <header className="sticky top-0 z-20 bg-white border-b border-stone-200 shadow-sm animate-slideDown">
        <div className="max-w-app landscape:max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
          <Link to="/" className="flex items-center gap-3 no-underline min-w-0">
            <div className="h-10 w-10 rounded-2xl bg-farm-600 flex items-center justify-center text-xl text-white shadow-sm shrink-0">
              🌾
            </div>
            <div className="min-w-0">
              <div className="font-bold text-[17px] leading-tight text-stone-800 truncate">{t.app}</div>
              <div className="text-[11px] text-stone-500 leading-tight truncate">{t.tagline}</div>
            </div>
          </Link>
          <div className="flex items-center gap-2 shrink-0">
            <div className="hidden sm:flex items-center gap-2 text-stone-500 text-sm">
              <span className="text-xs">🌐</span>
              <span className="text-xs font-medium">{t.lang}</span>
            </div>
            <select
              value={lang}
              onChange={e => setLang(e.target.value)}
              className="bg-stone-50 text-stone-700 rounded-xl px-3 py-1.5 text-sm font-medium border border-stone-200 focus:outline-none focus:border-farm-400 focus:ring-2 focus:ring-farm-100"
              aria-label={t.lang}
            >
              {LANGS.map(l => <option key={l.code} value={l.code}>{l.label}</option>)}
            </select>
            <Link to="/chat" className="h-9 w-9 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-center text-stone-600 hover:bg-stone-100 transition-colors">
              🔔
            </Link>
          </div>
        </div>
      </header>

      {/* Body: sidebar (landscape) + content */}
      <div className="max-w-app landscape:max-w-5xl mx-auto landscape:flex landscape:items-start landscape:gap-5 landscape:px-4">
        {/* Sidebar — Figma: white pill active green */}
        <nav className="hidden landscape:flex landscape:flex-col landscape:gap-1 landscape:w-52 landscape:shrink-0 landscape:sticky landscape:top-[64px] landscape:py-6" aria-label="Primary">
          <div className="bg-white rounded-3xl shadow-sm border border-stone-100 p-3 space-y-1">
            {NAV.map((item, idx) => {
              const active = loc.pathname === item.to
              return (
                <Link key={item.to} to={item.to} style={{ animationDelay: `${idx * 40}ms` }} className={`flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm font-medium transition-all duration-base ease-standard no-underline will-change-transform animate-fadeUp ${active ? 'bg-farm-600 text-white shadow-sm scale-[1.02]' : 'text-stone-600 hover:bg-stone-50 hover:translate-x-0.5'}`} aria-current={active ? 'page' : undefined}>
                  <span className="text-lg leading-none transition-transform duration-fast group-hover:scale-110" aria-hidden="true">{item.icon}</span>
                  <span className="truncate">{t[item.key]}</span>
                </Link>
              )
            })}
            <div className="pt-3 mt-1 border-t border-stone-100">
              <Link to="/soil" className={`flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm font-medium no-underline ${loc.pathname === '/soil' ? 'bg-farm-600 text-white' : 'text-stone-600 hover:bg-stone-50'}`}>
                <span className="text-lg">🧪</span><span>{t.soil}</span>
              </Link>
            </div>
          </div>
        </nav>

        {/* Content */}
        <main className="px-4 pt-4 pb-24 landscape:flex-1 landscape:min-w-0 landscape:px-0 landscape:pt-6 landscape:pb-6">{children}</main>
      </div>

      {/* Bottom nav — Figma mobile: white bar, green pill active */}
      <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-app bg-white border-t border-stone-200 px-2 pt-2 pb-[max(8px,env(safe-area-inset-bottom))] z-20 landscape:hidden shadow-[0_-4px_20px_rgba(0,0,0,0.04)]">
        <div className="flex justify-around gap-1">
          {NAV.map(item => {
            const active = loc.pathname === item.to
            return (
              <Link key={item.to} to={item.to} className={`flex flex-col items-center gap-0.5 flex-1 py-2 rounded-2xl text-xs font-medium transition-colors no-underline ${active ? 'bg-farm-600 text-white shadow-sm' : 'text-stone-500'}`} aria-current={active ? 'page' : undefined}>
                <span className="text-xl leading-none" aria-hidden="true">{item.icon}</span>
                <span className="text-[10px] leading-tight">{t[item.key]}</span>
              </Link>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
