import { createContext, useCallback, useContext, useEffect, useState } from 'react'

const AppCtx = createContext(null)
export const useApp = () => useContext(AppCtx)

// Reverse-geocode lat/lon → city name via Nominatim (free, no key)
async function reverseGeo(lat, lon) {
  try {
    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&zoom=10`, {
      headers: { 'Accept-Language': 'hi,en' },
    })
    const d = await r.json()
    return d.address?.city || d.address?.town || d.address?.village || d.address?.county || d.address?.state || ''
  } catch { return '' }
}

// Default fallback (Ahmedabad)
const FALLBACK = { lat: 23.03, lon: 72.58, name: 'Ahmedabad' }

export function AppProvider({ children }) {
  const [lang, setLang] = useState('hi')
  const [crop, setCrop] = useState('wheat')
  const [location, setLocation] = useState(FALLBACK)
  const [geoStatus, setGeoStatus] = useState('loading') // loading | granted | denied | error

  // Request geolocation on mount — high accuracy first, fallback to low
  useEffect(() => {
    if (!navigator.geolocation) { setGeoStatus('error'); return }

    const onSuccess = async (pos) => {
      const { latitude: lat, longitude: lon } = pos.coords
      const name = await reverseGeo(lat, lon)
      setLocation({ lat, lon, name: name || `${lat.toFixed(2)}, ${lon.toFixed(2)}` })
      setGeoStatus('granted')
    }

    const onHighError = () => {
      // Retry with low accuracy for faster response on Android
      navigator.geolocation.getCurrentPosition(onSuccess, onFinalError, {
        enableHighAccuracy: false, timeout: 5000, maximumAge: 600000,
      })
    }

    const onFinalError = (err) => {
      console.warn('Geolocation denied/error:', err.message)
      setGeoStatus(err.code === 1 ? 'denied' : 'error')
    }

    navigator.geolocation.getCurrentPosition(onSuccess, onHighError, {
      enableHighAccuracy: true, timeout: 5000, maximumAge: 300000,
    })
  }, [])

  return (
    <AppCtx.Provider value={{ lang, setLang, crop, setCrop, location, setLocation, geoStatus }}>
      {children}
    </AppCtx.Provider>
  )
}
