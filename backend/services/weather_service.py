"""
Weather service via Open-Meteo (free, no API key).
GET https://api.open-meteo.com/v1/forecast?latitude=..&longitude=..&current=..&daily=..

Adds irrigation / crop-management advice from temp + rain + humidity.
Caches in-memory for 30 min to avoid rate limits.
"""

import time
import structlog
from typing import Optional

logger = structlog.get_logger()
_CACHE = {}
_TTL = 30 * 60


async def get_weather(lat: float, lon: float, location: str = "") -> dict:
    key = f"{round(lat,2)},{round(lon,2)}"
    now = time.time()
    if key in _CACHE and now - _CACHE[key]["ts"] < _TTL:
        return _CACHE[key]["data"]
    try:
        import httpx
        url = ("https://api.open-meteo.com/v1/forecast"
               f"?latitude={lat}&longitude={lon}"
               "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
               "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum"
               "&timezone=auto&forecast_days=7")
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.get(url)
            r.raise_for_status()
            j = r.json()
        data = _parse(j, lat, lon, location or f"{lat},{lon}")
    except Exception as e:
        logger.warning("Weather API failed, fallback", error=str(e))
        data = _fallback(lat, lon, location)
    _CACHE[key] = {"ts": now, "data": data}
    return data


def _parse(j: dict, lat: float, lon: float, location: str) -> dict:
    cur = j.get("current", {})
    daily = j.get("daily", {})
    temp = cur.get("temperature_2m", 30.0)
    hum = cur.get("relative_humidity_2m", 60.0)
    rain = cur.get("precipitation", 0.0)
    wind = cur.get("wind_speed_10m", 10.0)
    code = cur.get("weather_code", 1)
    condition = _code_to_text(code)
    forecast = []
    times = daily.get("time", [])
    for i, d in enumerate(times):
        forecast.append({
            "date": d,
            "temp_min": (daily.get("temperature_2m_min") or [25])[i] if i < len(daily.get("temperature_2m_min", [])) else 25,
            "temp_max": (daily.get("temperature_2m_max") or [35])[i] if i < len(daily.get("temperature_2m_max", [])) else 35,
            "humidity": hum,
            "rainfall_probability": ((daily.get("precipitation_probability_max") or [0])[i] if i < len(daily.get("precipitation_probability_max", [])) else 0) / 100.0,
            "rainfall_amount": (daily.get("precipitation_sum") or [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
            "condition": condition if i == 0 else "forecast",
            "wind_speed": wind,
        })
    return {
        "location": location, "latitude": lat, "longitude": lon,
        "current": {"temperature": temp, "humidity": hum, "rainfall": rain,
                    "wind_speed": wind, "condition": condition,
                    "description": condition, "location": location},
        "forecast": forecast,
        "agricultural_advice": make_advice(temp, hum, rain, forecast),
        "source": "open-meteo",
    }


def _code_to_text(code: int) -> str:
    if code in (0,): return "sunny"
    if code in (1, 2): return "partly_cloudy"
    if code in (3,): return "cloudy"
    if code in (45, 48): return "foggy"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82): return "rainy"
    if code in (71, 73, 75, 77): return "snowy"
    if code in (95, 96, 99): return "stormy"
    return "partly_cloudy"


def make_advice(temp: float, hum: float, rain: float, forecast: list) -> list:
    adv = []
    rain_soon = any((f.get("rainfall_probability", 0) or 0) > 0.6 for f in forecast[:3])
    if rain_soon or rain > 2:
        adv.append("Rain expected - postpone irrigation and fertilizer spray by 2-3 days.")
        adv.append("Ensure field drainage; avoid waterlogging in vegetables.")
    else:
        adv.append("No heavy rain expected - irrigate early morning if topsoil is dry.")
    if temp and temp > 38:
        adv.append("Heat stress risk: light evening irrigation + mulching helps.")
    if hum and hum > 80:
        adv.append("High humidity: fungal disease risk. Scout leaves, avoid overhead watering.")
    if hum and hum < 30:
        adv.append("Dry air: increase irrigation frequency, watch for mites/aphids.")
    adv.append("Weather advice is guidance only - check sky before major operations.")
    return adv


def _fallback(lat: float, lon: float, location: str) -> dict:
    return {
        "location": location or f"{lat},{lon}", "latitude": lat, "longitude": lon,
        "current": {"temperature": 31.0, "humidity": 60.0, "rainfall": 0.0,
                    "wind_speed": 10.0, "condition": "unknown",
                    "description": "Offline estimate", "location": location},
        "forecast": [],
        "agricultural_advice": ["Weather service offline. Check local sky; irrigate only if topsoil dry."],
        "source": "fallback",
    }
