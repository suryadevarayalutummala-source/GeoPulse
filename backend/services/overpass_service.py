import json
import logging
import math
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests
from requests import RequestException

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

Coordinate = Tuple[float, float]
LocationPoint = Tuple[float, float]


class OverpassServiceError(Exception):
    """Base exception for Overpass service failures."""


class OverpassResponseError(OverpassServiceError):
    """Raised when the Overpass response is malformed or invalid."""


class OverpassService:
    """Service for executing Overpass API queries and normalizing results."""

    DEFAULT_HEADERS = {
        "User-Agent": "SmartInfraHackathon/1.0 (team@example.com)",
        "Accept": "application/json",
    }
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, user_agent: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        if user_agent:
            self.session.headers["User-Agent"] = user_agent

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> "OverpassService":
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        self.close()

    def _validate_search_input(self, latitude: float, longitude: float, radius: int) -> None:
        if not (-90.0 <= latitude <= 90.0):
            logger.error("Invalid latitude: %s", latitude)
            raise OverpassServiceError("latitude must be between -90 and 90")

        if not (-180.0 <= longitude <= 180.0):
            logger.error("Invalid longitude: %s", longitude)
            raise OverpassServiceError("longitude must be between -180 and 180")

        if radius <= 0:
            logger.error("Invalid radius: %s", radius)
            raise OverpassServiceError("radius must be a positive integer")

    def _haversine_distance(self, origin: LocationPoint, destination: LocationPoint) -> float:
        lat1, lon1 = origin
        lat2, lon2 = destination
        radians = math.radians
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(radians(lat1))
            * math.cos(radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371000.0 * c

    def _build_query(self, filters: Sequence[str], latitude: float, longitude: float, radius: int) -> str:
        query_parts: List[str] = []
        for filter_expr in filters:
            query_parts.append(f"node{filter_expr}(around:{radius},{latitude},{longitude});")
            query_parts.append(f"way{filter_expr}(around:{radius},{latitude},{longitude});")
            query_parts.append(f"relation{filter_expr}(around:{radius},{latitude},{longitude});")

        query_body = "\n".join(query_parts)
        return f"[out:json][timeout:25];\n(\n{query_body}\n);\nout center tags;"

    def _execute_query(self, query: str) -> Dict[str, Any]:
        max_attempts = 3
        backoff_seconds = 1.0

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.post(OVERPASS_API_URL, data={"data": query}, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
            except RequestException as exc:
                status_code = getattr(exc.response, "status_code", None)
                if status_code in {429, 504} and attempt < max_attempts:
                    logger.warning(
                        "Overpass request got status %s, retrying attempt %s/%s.",
                        status_code,
                        attempt,
                        max_attempts,
                    )
                    time.sleep(backoff_seconds * attempt)
                    continue

                logger.error("Overpass API request failed: %s", exc)
                return {"elements": []}
            except json.JSONDecodeError as exc:
                logger.error("Failed to decode Overpass API response: %s", exc)
                return {"elements": []}

            if not isinstance(payload, dict) or "elements" not in payload:
                logger.error("Overpass API response missing elements field: %s", payload)
                return {"elements": []}

            return payload

        return {"elements": []}

    def _normalize_element(self, element: Dict[str, Any], origin: LocationPoint) -> Optional[Dict[str, Any]]:
        tags = element.get("tags") or {}
        lat = element.get("lat")
        lon = element.get("lon")
        center = element.get("center") or {}

        if lat is None or lon is None:
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            return None

        item = {
            "id": element.get("id"),
            "type": element.get("type"),
            "name": tags.get("name") or "Unknown",
            "latitude": float(lat),
            "longitude": float(lon),
            "nearest_distance_m": self._haversine_distance(origin, (float(lat), float(lon))),
            "distance_km": round(self._haversine_distance(origin, (float(lat), float(lon))) / 1000.0, 2),
        }
        return item

    def _search(self, latitude: float, longitude: float, radius: int, filters: Sequence[str]) -> Dict[str, Any]:
        self._validate_search_input(latitude, longitude, radius)
        query = self._build_query(filters, latitude, longitude, radius)
        payload = self._execute_query(query)

        elements = payload.get("elements")
        if not isinstance(elements, list):
            logger.warning("Overpass response elements field is not a list.")
            raise OverpassResponseError("Overpass response elements field is invalid")

        items: List[Dict[str, Any]] = []
        for element in elements:
            normalized = self._normalize_element(element, (latitude, longitude))
            if normalized:
                items.append(normalized)

        items.sort(key=lambda row: row["nearest_distance_m"])

        names = [item["name"] for item in items if item["name"]]
        coordinates = [
            {"latitude": item["latitude"], "longitude": item["longitude"]}
            for item in items
        ]
        nearest_distance = items[0]["nearest_distance_m"] if items else None

        result: Dict[str, Any] = {
            "count": len(items),
            "names": names,
            "coordinates": coordinates,
            "nearest_distance_m": nearest_distance,
            "items": items,
        }

        logger.info(
            "Overpass query returned %d items for location (%s, %s) and radius %s.",
            len(items),
            latitude,
            longitude,
            radius,
        )
        return result

    def get_schools(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return nearby schools from Overpass within the given radius."""
        return self._search(
            latitude,
            longitude,
            radius,
            [
                "[\"amenity\"=\"school\"]",
                "[\"amenity\"=\"college\"]",
                "[\"amenity\"=\"university\"]",
                "[\"amenity\"=\"kindergarten\"]",
            ],
        )

    def get_hospitals(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return nearby hospitals from Overpass within the given radius."""
        return self._search(
            latitude,
            longitude,
            radius,
            [
                "[\"amenity\"=\"hospital\"]",
                "[\"amenity\"=\"clinic\"]",
                "[\"amenity\"=\"doctors\"]",
            ],
        )

    def get_parks(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return nearby parks from Overpass within the given radius."""
        return self._search(latitude, longitude, radius, ["[\"leisure\"=\"park\"]"])

    def get_bus_stops(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return nearby bus stops from Overpass within the given radius."""
        return self._search(latitude, longitude, radius, ["[\"highway\"=\"bus_stop\"]"])

    def get_metro(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return nearby metro transit features from Overpass within the given radius."""
        filters = [
            "[\"railway\"=\"subway_entrance\"]",
            "[\"public_transport\"=\"stop_position\"][\"subway\"=\"yes\"]",
            "[\"station\"=\"subway\"]",
            "[\"railway\"=\"station\"]",
            "[\"station\"=\"light_rail\"]",
        ]
        return self._search(latitude, longitude, radius, filters)

    def get_shopping_malls(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return nearby shopping malls from Overpass within the given radius."""
        filters = [
            "[\"shop\"=\"mall\"]",
            "[\"leisure\"=\"shopping_centre\"]",
        ]
        return self._search(latitude, longitude, radius, filters)

    def get_buyer_context(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return buyer-focused amenities data using live Overpass queries and nearest-distance sorting."""
        schools = self.get_schools(latitude, longitude, radius)
        hospitals = self.get_hospitals(latitude, longitude, radius)
        metro = self.get_metro(latitude, longitude, radius)
        bus_stops = self.get_bus_stops(latitude, longitude, radius)
        parks = self.get_parks(latitude, longitude, radius)
        shopping = self.get_shopping_malls(latitude, longitude, radius)

        transit_items = []
        for category in (metro, bus_stops):
            transit_items.extend(category.get("items", []))
        transit_items = sorted(transit_items, key=lambda item: item["nearest_distance_m"])

        nearest_hospital_item = None
        if hospitals.get("items"):
            nearest_hospital_item = hospitals["items"][0]
        nearest_hospital_km = round(nearest_hospital_item["distance_km"], 2) if nearest_hospital_item else 0.0

        return {
            "schools_nearby": schools.get("count", 0),
            "hospitals_nearby": hospitals.get("count", 0),
            "transit_hubs_nearby": len(transit_items),
            "shopping_centres_nearby": shopping.get("count", 0),
            "parks_nearby": parks.get("count", 0),
            "nearest_hospital_km": nearest_hospital_km,
            "parks": parks,
            "shopping_centres": shopping,
            "top_nearby_schools": [
                {
                    "name": item["name"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "distance_km": item["distance_km"],
                }
                for item in schools.get("items", [])[:5]
            ],
            "top_nearby_hospitals": [
                {
                    "name": item["name"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "distance_km": item["distance_km"],
                }
                for item in hospitals.get("items", [])[:5]
            ],
            "top_nearby_shopping_centres": [
                {
                    "name": item["name"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "distance_km": item["distance_km"],
                }
                for item in shopping.get("items", [])[:5]
            ],
            "transit_hubs": transit_items,
        }

    def get_amenities(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Return multiple amenity categories in a single Overpass query."""
        self._validate_search_input(latitude, longitude, radius)

        category_filters = {
            "schools": [
                "[\"amenity\"=\"school\"]",
                "[\"amenity\"=\"college\"]",
                "[\"amenity\"=\"university\"]",
                "[\"amenity\"=\"kindergarten\"]",
            ],
            "hospitals": [
                "[\"amenity\"=\"hospital\"]",
                "[\"amenity\"=\"clinic\"]",
                "[\"amenity\"=\"doctors\"]",
            ],
            "parks": ["[\"leisure\"=\"park\"]"],
            "bus_stops": ["[\"highway\"=\"bus_stop\"]"],
            "metro": [
                "[\"railway\"=\"subway_entrance\"]",
                "[\"public_transport\"=\"stop_position\"][\"subway\"=\"yes\"]",
                "[\"station\"=\"subway\"]",
                "[\"railway\"=\"station\"]",
                "[\"station\"=\"light_rail\"]",
            ],
            "shopping_malls": [
                "[\"shop\"=\"mall\"]",
                "[\"leisure\"=\"shopping_centre\"]",
            ],
        }

        all_filters = [expr for filters in category_filters.values() for expr in filters]
        payload = self._execute_query(self._build_query(all_filters, latitude, longitude, radius))

        elements = payload.get("elements")
        if not isinstance(elements, list):
            logger.warning("Overpass response elements field is not a list.")
            raise OverpassResponseError("Overpass response elements field is invalid")

        categories = {category: [] for category in category_filters}
        for element in elements:
            tags = element.get("tags", {}) or {}
            category = self._categorize_amenity(tags)
            if category is None:
                continue
            normalized = self._normalize_element(element, (latitude, longitude))
            if normalized:
                categories[category].append(normalized)

        results: Dict[str, Any] = {}
        for category, items in categories.items():
            items.sort(key=lambda row: row["nearest_distance_m"])
            results[category] = {
                "count": len(items),
                "names": [item["name"] for item in items],
                "coordinates": [{"latitude": item["latitude"], "longitude": item["longitude"]} for item in items],
                "nearest_distance_m": items[0]["nearest_distance_m"] if items else None,
                "items": items,
            }

        logger.info(
            "Overpass multi-category query returned counts=%s for location (%s, %s) and radius %s.",
            {k: len(v) for k, v in categories.items()},
            latitude,
            longitude,
            radius,
        )
        return results

    def _categorize_amenity(self, tags: Dict[str, Any]) -> Optional[str]:
        amenity = tags.get("amenity")
        if amenity in {"school", "college", "university", "kindergarten"}:
            return "schools"
        if amenity in {"hospital", "clinic", "doctors"}:
            return "hospitals"
        if tags.get("leisure") == "park":
            return "parks"
        if tags.get("highway") == "bus_stop":
            return "bus_stops"
        if tags.get("railway") in {"subway_entrance", "station"} or tags.get("station") in {"subway", "light_rail"}:
            return "metro"
        if tags.get("shop") == "mall" or tags.get("leisure") == "shopping_centre":
            return "shopping_malls"
        return None
