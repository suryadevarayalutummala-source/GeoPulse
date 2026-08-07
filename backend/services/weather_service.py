from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class WeatherServiceError(Exception):
    """Raised when the OpenWeather service cannot be reached or configured."""


class WeatherService:
    """Thin wrapper around the OpenWeather API for air quality and weather context."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 10.0) -> None:
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
        self.timeout = timeout
        self.session = requests.Session()

    def get_air_quality(self, latitude: float, longitude: float) -> Dict[str, Any]:
        if not self.api_key:
            raise WeatherServiceError("OpenWeather API key is not configured")

        url = f"{self.BASE_URL}/air_pollution"
        params = {"lat": latitude, "lon": longitude, "appid": self.api_key}
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()

        list_items = payload.get("list") or []
        main_item = list_items[0] if list_items else {}
        air_quality = main_item.get("main") or {}
        components = main_item.get("components") or {}

        return {
            "air_quality_index": int(air_quality.get("aqi", 0)),
            "pm2_5": round(float(components.get("pm2_5", 0.0)), 2),
            "pm10": round(float(components.get("pm10", 0.0)), 2),
        }

    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        if not self.api_key:
            raise WeatherServiceError("OpenWeather API key is not configured")

        url = f"{self.BASE_URL}/weather"
        params = {"lat": latitude, "lon": longitude, "appid": self.api_key, "units": "metric"}
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()

        main = payload.get("main") or {}
        return {
            "temperature_c": round(float(main.get("temp", 0.0)), 1),
            "humidity_percent": int(main.get("humidity", 0)),
        }

    def get_environment_context(self, latitude: float, longitude: float) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "air_quality_index": None,
            "pm2_5": None,
            "pm10": None,
            "temperature_c": None,
            "humidity_percent": None,
        }
        try:
            air_quality = self.get_air_quality(latitude, longitude)
            context.update(air_quality)
        except (WeatherServiceError, requests.RequestException) as exc:
            logger.warning("OpenWeather air quality request failed: %s", exc)

        try:
            weather = self.get_weather(latitude, longitude)
            context.update(weather)
        except (WeatherServiceError, requests.RequestException) as exc:
            logger.warning("OpenWeather weather request failed: %s", exc)

        return context
