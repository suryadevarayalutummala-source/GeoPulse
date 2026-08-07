import json
import logging
import math
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from requests import RequestException, Response

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

GeocodeResult = Dict[str, Optional[str]]

SUPPORTED_LOCALITIES = [
    "Old City (Charminar / Malakpet)",
    "Banjara Hills / Jubilee Hills",
    "Gachibowli / HITEC City",
    "Kokapet / Narsingi",
    "Gandipet / Manikonda",
    "Kompally / Medchal",
    "Uppal / LB Nagar",
    "Shamshabad",
]

LOCALITY_ALIASES_FILE = Path(__file__).resolve().parents[1] / "data" / "locality_aliases.json"
PLOTS_FILE = Path(__file__).resolve().parents[1] / "data" / "plots_final.json"

LOCALITY_REFERENCE_POINTS = {
    "Old City (Charminar / Malakpet)": (17.3653, 78.4741),
    "Banjara Hills / Jubilee Hills": (17.4219, 78.4115),
    "Gachibowli / HITEC City": (17.4474, 78.3811),
    "Kokapet / Narsingi": (17.3952, 78.3434),
    "Gandipet / Manikonda": (17.3920, 78.3836),
    "Kompally / Medchal": (17.5259, 78.4928),
    "Uppal / LB Nagar": (17.3579, 78.5336),
    "Shamshabad": (17.2403, 78.4303),
}


class GeocoderError(Exception):
    """Base exception for geocoder failures."""


class GeocoderServiceError(GeocoderError):
    """Raised when the reverse geocoding request fails."""


class GeocoderService:
    """OpenStreetMap Nominatim reverse geocoding service with Hyderabad locality matching."""

    BASE_URL = "https://nominatim.openstreetmap.org/reverse"
    DEFAULT_TIMEOUT = 10.0
    DEFAULT_HEADERS = {
        "User-Agent": "SmartInfraHackathon/1.0 (team@example.com)",
        "Accept-Language": "en",
    }
    MAX_RETRIES = 3

    def __init__(self, user_agent: str = "SmartInfraHackathon/1.0 (team@example.com)", timeout: float = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.session.headers["User-Agent"] = user_agent
        self.aliases = self._load_locality_aliases()

    def _validate_coordinates(self, latitude: float, longitude: float) -> None:
        if not (-90.0 <= latitude <= 90.0):
            logger.error("Invalid latitude value: %s", latitude)
            raise GeocoderServiceError("latitude must be between -90 and 90")
        if not (-180.0 <= longitude <= 180.0):
            logger.error("Invalid longitude value: %s", longitude)
            raise GeocoderServiceError("longitude must be between -180 and 180")

    def _extract_address(self, response: Response) -> GeocodeResult:
        payload = response.json()
        address = payload.get("address", {}) or {}
        locality = (
            address.get("suburb")
            or address.get("city_district")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
        )
        return {
            "city": (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
            ),
            "district": (
                address.get("county")
                or address.get("state_district")
                or address.get("suburb")
            ),
            "state": address.get("state"),
            "country": address.get("country"),
            "display_name": payload.get("display_name"),
            "postcode": address.get("postcode"),
            "locality": locality,
        }

    def _fallback_locality(self, latitude: float, longitude: float) -> Optional[str]:
        nearest_name = None
        nearest_distance = float("inf")
        for name, reference in LOCALITY_REFERENCE_POINTS.items():
            ref_lat, ref_lon = reference
            distance = ((latitude - ref_lat) ** 2 + (longitude - ref_lon) ** 2) ** 0.5
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_name = name
        return nearest_name

    def detect_locality(self, latitude: float, longitude: float) -> Optional[str]:
        """Detect the supported Hyderabad locality from coordinates."""
        self._validate_coordinates(latitude, longitude)
        try:
            geocode = self.reverse_geocode(latitude, longitude)
            raw_locality = (geocode.get("locality") or geocode.get("city") or "").strip()
            if raw_locality:
                return self._normalize_locality(raw_locality)
        except GeocoderServiceError:
            pass
        return self._fallback_locality(latitude, longitude)

    def _load_locality_aliases(self) -> Dict[str, list[str]]:
        if not LOCALITY_ALIASES_FILE.exists():
            return {}
        try:
            payload = json.loads(LOCALITY_ALIASES_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(payload, dict):
            return {}

        aliases: Dict[str, list[str]] = {}
        for cluster_name, values in payload.items():
            if isinstance(cluster_name, str) and isinstance(values, list):
                aliases[cluster_name] = [str(item).strip() for item in values if str(item).strip()]
        return aliases

    def _normalize_locality(self, locality: str) -> Optional[str]:
        lowered = locality.lower()
        for candidate in SUPPORTED_LOCALITIES:
            if lowered in candidate.lower():
                return candidate
        for cluster_name, aliases in self.aliases.items():
            if any(alias.lower() in lowered for alias in aliases):
                return cluster_name
        if "malakpet" in lowered or "charminar" in lowered:
            return "Old City (Charminar / Malakpet)"
        if "banjara" in lowered or "jubilee" in lowered:
            return "Banjara Hills / Jubilee Hills"
        if "gachibowli" in lowered or "hitec" in lowered or "hitech" in lowered:
            return "Gachibowli / HITEC City"
        if "kokapet" in lowered or "narsingi" in lowered:
            return "Kokapet / Narsingi"
        if "manikonda" in lowered or "gandipet" in lowered:
            return "Gandipet / Manikonda"
        if "kompally" in lowered or "medchal" in lowered:
            return "Kompally / Medchal"
        if "uppal" in lowered or "lb nagar" in lowered or "lbnagar" in lowered:
            return "Uppal / LB Nagar"
        if "shamshabad" in lowered:
            return "Shamshabad"
        return None

    def _resolve_cluster_from_locality(self, locality: str) -> Optional[str]:
        if not locality:
            return None
        lowered = locality.strip().lower()
        for candidate in SUPPORTED_LOCALITIES:
            if lowered in candidate.lower() or candidate.lower() in lowered:
                return candidate
        for cluster_name, aliases in self.aliases.items():
            for alias in aliases:
                if not alias:
                    continue
                alias_lower = alias.lower()
                if lowered == alias_lower or lowered in alias_lower or alias_lower in lowered:
                    return cluster_name
        return None

    def _load_plot_catalog(self) -> list[dict]:
        if not PLOTS_FILE.exists():
            return []
        try:
            payload = json.loads(PLOTS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        return [plot for plot in payload if isinstance(plot, dict)]

    def _haversine_distance(self, latitude: float, longitude: float, target_latitude: float, target_longitude: float) -> float:
        radius_km = 6371.0
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(target_latitude)
        lon2 = math.radians(target_longitude)
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c

    def _select_nearest_plot(self, latitude: float, longitude: float, cluster_name: Optional[str]) -> Dict[str, Optional[object]]:
        if not cluster_name:
            return {
                "selected_plot": None,
                "cluster": None,
                "landmark": None,
                "latitude": None,
                "longitude": None,
            }

        best_plot = None
        best_distance = float("inf")
        for plot in self._load_plot_catalog():
            if plot.get("cluster") != cluster_name:
                continue
            coordinates = plot.get("coordinates") or {}
            plot_latitude = coordinates.get("latitude")
            plot_longitude = coordinates.get("longitude")
            if not isinstance(plot_latitude, (int, float)) or not isinstance(plot_longitude, (int, float)):
                continue
            distance = self._haversine_distance(latitude, longitude, float(plot_latitude), float(plot_longitude))
            if distance < best_distance:
                best_distance = distance
                best_plot = plot

        if not best_plot:
            return {
                "selected_plot": None,
                "cluster": cluster_name,
                "landmark": None,
                "latitude": None,
                "longitude": None,
            }

        coordinates = best_plot.get("coordinates") or {}
        return {
            "selected_plot": best_plot,
            "cluster": cluster_name,
            "landmark": best_plot.get("landmark"),
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
        }

    def reverse_geocode(self, latitude: float, longitude: float) -> GeocodeResult:
        """Reverse geocode a latitude and longitude to structured location data."""
        self._validate_coordinates(latitude, longitude)

        params = {
            "format": "jsonv2",
            "lat": latitude,
            "lon": longitude,
            "addressdetails": 1,
            "zoom": 18,
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = self._extract_address(response)
            raw_locality = (result.get("locality") or result.get("city") or "").strip()
            detected_locality = self._normalize_locality(raw_locality)
            cluster_name = self._resolve_cluster_from_locality(raw_locality) or detected_locality
            if detected_locality:
                result["matched_locality"] = detected_locality
            if cluster_name:
                result["cluster"] = cluster_name
            result.update(self._select_nearest_plot(latitude, longitude, cluster_name or detected_locality))
            logger.info(
                "Reverse geocode successful for (%s, %s): %s",
                latitude,
                longitude,
                result,
            )
            return result
        except RequestException as exc:
            logger.error(
                "Nominatim reverse geocode request failed for (%s, %s): %s",
                latitude,
                longitude,
                exc,
            )
        except ValueError as exc:
            logger.error("Invalid JSON returned by Nominatim: %s", exc)

        fallback_locality = self._fallback_locality(latitude, longitude)
        fallback_cluster = self._resolve_cluster_from_locality(fallback_locality or "") or fallback_locality
        fallback_result: GeocodeResult = {
            "city": fallback_locality,
            "district": None,
            "state": None,
            "country": None,
            "display_name": fallback_locality or "Unknown",
            "postcode": None,
            "locality": fallback_locality,
            "matched_locality": fallback_locality,
            "cluster": fallback_cluster,
        }
        fallback_result.update(self._select_nearest_plot(latitude, longitude, fallback_cluster))
        return fallback_result

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()
