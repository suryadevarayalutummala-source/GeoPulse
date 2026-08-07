"""
POST /api/v1/analyze-location — concurrent amenity + soil + market + legal risk fuse.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from config.geo_reference_points import GEO_REFERENCE_POINTS
from services.amenity_service import fetch_nearby_amenities
from services.geo_validation import validate_hyderabad_coords
from services.legal_risk_service import evaluate_legal_and_environmental_risks
from services.market_grounding_service import get_live_market_context
from services.rate_limit import limiter
from services.soil_interpolation_service import estimate_soil_properties

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["location-analysis"])


class AnalyzeLocationPayload(BaseModel):
    """Map click payload — lon/lat (GeoJSON order in naming)."""

    lon: float = Field(..., description="Longitude (e.g. 78.37)")
    lat: float = Field(..., description="Latitude (e.g. 17.44)")
    locality: str | None = None


def _nearest_locality(lon: float, lat: float) -> str:
    best_name = "Hyderabad"
    best_d = float("inf")
    for p in GEO_REFERENCE_POINTS:
        dlat = (lat - p["latitude"]) * 111.0
        dlon = (lon - p["longitude"]) * 111.0 * 0.95
        d = (dlat * dlat + dlon * dlon) ** 0.5
        if d < best_d:
            best_d = d
            best_name = p["locality"]
    return best_name


def _run_soil(lon: float, lat: float) -> dict[str, Any]:
    return estimate_soil_properties(longitude=lon, latitude=lat)


def _run_market(locality: str, lon: float, lat: float) -> dict[str, Any]:
    return get_live_market_context(locality, lat=lat, lon=lon)


@router.post("/analyze-location")
@limiter.limit("8/minute")
async def analyze_location(request: Request, payload: AnalyzeLocationPayload):
    _ = request
    validate_hyderabad_coords(longitude=payload.lon, latitude=payload.lat)

    locality = payload.locality or _nearest_locality(payload.lon, payload.lat)

    try:
        amenities_task = fetch_nearby_amenities(payload.lat, payload.lon, radius_m=2000)
        soil_task = asyncio.to_thread(_run_soil, payload.lon, payload.lat)
        market_task = asyncio.to_thread(_run_market, locality, payload.lon, payload.lat)

        amenities, soil, market = await asyncio.gather(
            amenities_task,
            soil_task,
            market_task,
            return_exceptions=True,
        )

        if isinstance(amenities, Exception):
            logger.exception("amenities failed: %s", type(amenities).__name__)
            amenities = {
                "hospitals_1km": 0,
                "schools_1km": 0,
                "metro_stations_2km": 0,
                "water_bodies": [],
                "locality_hint": None,
            }
        if isinstance(soil, Exception):
            logger.exception("soil failed: %s", type(soil).__name__)
            soil = {
                "bearing_capacity_kpa": 0,
                "water_table_depth_m": 0,
                "soil_type": "Unknown",
            }
        if isinstance(market, Exception):
            logger.exception("market failed: %s", type(market).__name__)
            market = {
                "avg_price_sqft": "Data unavailable",
                "rental_yield": "N/A",
                "growth_trend": "Unknown",
                "legal_notices": [],
            }

        if amenities.get("locality_hint") and not payload.locality:
            locality = amenities["locality_hint"]

        legality = evaluate_legal_and_environmental_risks(
            lon=payload.lon,
            lat=payload.lat,
            locality=locality,
            nearby_water_bodies=amenities.get("water_bodies") or [],
        )

        return {
            "location": {
                "lon": payload.lon,
                "lat": payload.lat,
                "locality": locality,
                # GeoJSON / Mapbox helper (always [lon, lat])
                "geojson_position": [payload.lon, payload.lat],
            },
            "legality_risk": {
                "risk_level": legality["risk_level"],
                "marker_color": legality["marker_color"],
                "flags": legality["flags"],
                "map_buffers": legality.get("map_buffers") or [],
            },
            "soil_profile": {
                "bearing_capacity_kpa": soil.get("bearing_capacity_kpa"),
                "water_table_depth_m": soil.get("water_table_depth_m"),
                "soil_type": soil.get("soil_type"),
                "estimation_note": soil.get("estimation_note"),
            },
            "market_trends": {
                "avg_price_sqft": market.get("avg_price_sqft"),
                "rental_yield": market.get("rental_yield"),
                "growth_trend": market.get("growth_trend"),
                "legal_notices": market.get("legal_notices") or [],
                "source_note": market.get("source_note"),
            },
            "amenities_summary": {
                "hospitals_1km": amenities.get("hospitals_1km", 0),
                "schools_1km": amenities.get("schools_1km", 0),
                "metro_stations_2km": amenities.get("metro_stations_2km", 0),
            },
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("analyze-location pipeline failed")
        raise HTTPException(status_code=500, detail="Unable to analyze location") from None
