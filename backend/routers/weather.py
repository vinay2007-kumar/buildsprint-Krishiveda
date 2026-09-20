"""Weather router: GET /api/weather?lat=&lon=&location="""

from fastapi import APIRouter, Query
from backend.services import weather_service

router = APIRouter()


@router.get("", response_model=None)
async def weather(lat: float = Query(23.03, description="Latitude (default Ahmedabad)"),
                  lon: float = Query(72.58, description="Longitude"),
                  location: str = Query("", description="Village/district name")):
    data = await weather_service.get_weather(lat, lon, location)
    return {"success": True, "data": data}
