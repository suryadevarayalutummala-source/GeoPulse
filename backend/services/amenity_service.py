"""
OpenStreetMap / Overpass amenity + water-body fetch for a map click.

Hackathon note: Overpass is best-effort and may rate-limit; always fail soft.
Production replacement: cached tile/DB of HMDA amenities + official water layers.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

_EMPTY = {
    "hospitals_1km": 0,
    "schools_1km": 0,
    "metro_stations_2km": 0,
    "transit_stops_2km": 0,
    "commercial_2km": 0,
    "water_bodies": [],
    "locality_hint": None,
}


def _build_query(lat: float, lon: float, radius_m: int) -> str:
    # Two radii: 1000m for schools/hospitals counts, radius_m (default 2000) for rest.
    r = max(radius_m, 500)
    return f"""
[out:json][timeout:25];
(
  node["amenity"="hospital"](around:1000,{lat},{lon});
  way["amenity"="hospital"](around:1000,{lat},{lon});
  node["amenity"="school"](around:1000,{lat},{lon});
  way["amenity"="school"](around:1000,{lat},{lon});
  node["railway"="station"](around:{r},{lat},{lon});
  node["station"="subway"](around:{r},{lat},{lon});
  node["public_transport"="station"](around:{r},{lat},{lon});
  node["highway"="bus_stop"](around:{r},{lat},{lon});
  node["shop"="mall"](around:{r},{lat},{lon});
  node["landuse"="commercial"](around:{r},{lat},{lon});
  way["landuse"="commercial"](around:{r},{lat},{lon});
  way["natural"="water"](around:{r},{lat},{lon});
  relation["natural"="water"](around:{r},{lat},{lon});
  way["waterway"~"river|stream|canal|drain"](around:{r},{lat},{lon});
);
out center tags;
""".strip()


def _as_water_body(el: dict[str, Any]) -> dict[str, Any] | None:
    tags = el.get("tags") or {}
    natural = tags.get("natural")
    waterway = tags.get("waterway")
    if natural != "water" and not waterway:
        return None
    center = el.get("center") or {}
    lat = el.get("lat", center.get("lat"))
    lon = el.get("lon", center.get("lon"))
    if lat is None or lon is None:
        return None
    return {
        "id": el.get("id"),
        "name": tags.get("name") or tags.get("water") or waterway or "water",
        "lat": float(lat),
        "lon": float(lon),
        "water": tags.get("water"),
        "waterway": waterway,
        "tags": tags,
        "geometry": None,  # center-based distance; upgrade when full geometry fetched
    }


async def fetch_nearby_amenities(
    lat: float,
    lon: float,
    radius_m: int = 2000,
) -> dict[str, Any]:
    query = _build_query(lat, lon, radius_m)
    elements: list[dict] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        last_err: Exception | None = None
        for url in OVERPASS_URLS:
            try:
                resp = await client.post(url, data={"data": query})
                resp.raise_for_status()
                elements = (resp.json() or {}).get("elements") or []
                last_err = None
                break
            except Exception as exc:
                last_err = exc
                logger.warning("Overpass failed via %s: %s", url, type(exc).__name__)
        if last_err and not elements:
            logger.exception("All Overpass endpoints failed")
            return dict(_EMPTY)

    hospitals = 0
    schools = 0
    metro = 0
    transit = 0
    commercial = 0
    water_bodies: list[dict] = []
    locality_hint = None

    for el in elements:
        tags = el.get("tags") or {}
        amenity = tags.get("amenity")
        if amenity == "hospital":
            hospitals += 1
        elif amenity == "school":
            schools += 1
        if tags.get("railway") == "station" or tags.get("station") == "subway":
            metro += 1
        if tags.get("highway") == "bus_stop" or tags.get("public_transport") == "station":
            transit += 1
        if tags.get("shop") == "mall" or tags.get("landuse") == "commercial":
            commercial += 1
        if tags.get("place") in ("suburb", "neighbourhood", "locality") and tags.get("name"):
            locality_hint = locality_hint or tags["name"]

        water = _as_water_body(el)
        if water:
            water_bodies.append(water)

    return {
        "hospitals_1km": hospitals,
        "schools_1km": schools,
        "metro_stations_2km": metro,
        "transit_stops_2km": transit,
        "commercial_2km": commercial,
        "water_bodies": water_bodies,
        "locality_hint": locality_hint,
    }
