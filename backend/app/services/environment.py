import os
import time
from typing import Any

import httpx
from fastapi import HTTPException


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
_cache: dict[str, tuple[float, dict[str, Any]]] = {}


async def _get(client: httpx.AsyncClient, url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.json()


async def fetch_environment(city: str, latitude: float | None = None, longitude: float | None = None) -> dict[str, Any]:
    cache_key = f"{city.casefold()}:{latitude}:{longitude}"
    cached = _cache.get(cache_key)
    cache_seconds = int(os.getenv("OPEN_METEO_CACHE_SECONDS", "300"))
    if cached and time.monotonic() - cached[0] < cache_seconds:
        return cached[1]

    timeout = float(os.getenv("OPEN_METEO_TIMEOUT_SECONDS", "8"))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if latitude is None or longitude is None:
                geocoding = await _get(client, GEOCODING_URL, {"name": city, "count": 1, "language": "en", "format": "json"})
                results = geocoding.get("results") or []
                if not results:
                    raise HTTPException(status_code=404, detail={"code": "city_not_found", "message": f"No location found for '{city}'."})
                location = results[0]
                latitude, longitude = location["latitude"], location["longitude"]
                resolved_city = ", ".join(part for part in (location.get("name"), location.get("country")) if part)
            else:
                resolved_city = city

            air_params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi",
                "hourly": "pm2_5,pm10,us_aqi,european_aqi",
                "past_days": 1,
                "forecast_days": 1,
                "timezone": "auto",
            }
            weather_params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation",
                "timezone": "auto",
            }
            import asyncio
            air, weather = await asyncio.gather(
                _get(client, AIR_URL, air_params),
                _get(client, WEATHER_URL, weather_params),
            )
    except HTTPException:
        raise
    except (httpx.HTTPError, ValueError, KeyError) as error:
        raise HTTPException(status_code=503, detail={"code": "environment_data_unavailable", "message": "Open-Meteo data is temporarily unavailable. Simulation remains available."}) from error

    current = air.get("current") or {}
    weather_current = weather.get("current") or {}
    units = air.get("current_units") or {}
    weather_units = weather.get("current_units") or {}
    pollutants = [
        {"key": key, "label": label, "value": current.get(key), "unit": units.get(key, ""), "status": "live" if current.get(key) is not None else "unavailable"}
        for key, label in (("pm2_5", "PM2.5"), ("pm10", "PM10"), ("carbon_monoxide", "Carbon monoxide"), ("nitrogen_dioxide", "Nitrogen dioxide"), ("sulphur_dioxide", "Sulphur dioxide"), ("ozone", "Ozone"))
    ]
    result = {
        "status": "live",
        "city": resolved_city,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "updated_at": current.get("time"),
        "source": "Open-Meteo Air Quality API and Forecast API",
        "aqi": {
            "us": {"value": current.get("us_aqi"), "unit": "US AQI", "status": "live" if current.get("us_aqi") is not None else "unavailable"},
            "european": {"value": current.get("european_aqi"), "unit": "European AQI", "status": "live" if current.get("european_aqi") is not None else "unavailable"},
        },
        "pollutants": pollutants,
        "weather": {
            key: {"value": weather_current.get(key), "unit": weather_units.get(key, ""), "status": "live" if weather_current.get(key) is not None else "unavailable"}
            for key in ("temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation")
        },
        "hourly": air.get("hourly") or {"time": [], "pm2_5": [], "pm10": [], "us_aqi": [], "european_aqi": []},
    }
    _cache[cache_key] = (time.monotonic(), result)
    return result