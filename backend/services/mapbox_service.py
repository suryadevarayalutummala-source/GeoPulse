from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class MapboxServiceError(Exception):
    """Raised when the Mapbox Matrix API cannot be reached or configured."""


class MapboxService:
    """Wrapper around the Mapbox Matrix API for commute and travel times."""

    BASE_URL = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving"

    def __init__(self, access_token: Optional[str] = None, timeout: float = 10.0) -> None:
        self.access_token = access_token or os.getenv("MAPBOX_ACCESS_TOKEN")
        self.timeout = timeout
        self.session = requests.Session()

    def _build_coordinates(self, longitude: float, latitude: float) -> List[List[float]]:
        return [[longitude, latitude]]

    def _build_matrix_url(self, origins: Sequence[Sequence[float]], destinations: Sequence[Sequence[float]]) -> str:
        if not self.access_token:
            raise MapboxServiceError("Mapbox access token is not configured")
        origin_param = ";".join(f"{lon},{lat}" for lon, lat in origins)
        destination_param = ";".join(f"{lon},{lat}" for lon, lat in destinations)
        return f"{self.BASE_URL}/{origin_param};{destination_param}?access_token={self.access_token}"

    def get_travel_times(self, latitude: float, longitude: float) -> Dict[str, Any]:
        if not self.access_token:
            raise MapboxServiceError("Mapbox access token is not configured")

        city_center = [78.4867, 17.3850]
        airport = [78.4298, 17.2403]
        metro = [78.3811, 17.4474]

        origins = self._build_coordinates(longitude, latitude)
        destinations = [city_center, airport, metro]
        url = self.BASE_URL
        params = {
            "access_token": self.access_token,
            "destinations": ";".join(f"{lon},{lat}" for lon, lat in destinations),
            "origins": ";".join(f"{lon},{lat}" for lon, lat in origins),
        }

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        durations = payload.get("durations") or []
        if not durations:
            return {
                "commute_time_to_city_center_min": None,
                "travel_time_to_airport": None,
                "travel_time_to_nearest_metro": None,
            }

        row = durations[0] if durations else []
        return {
            "commute_time_to_city_center_min": int(round(float(row[0]) / 60.0)) if len(row) > 0 else None,
            "travel_time_to_airport": int(round(float(row[1]) / 60.0)) if len(row) > 1 else None,
            "travel_time_to_nearest_metro": int(round(float(row[2]) / 60.0)) if len(row) > 2 else None,
        }
