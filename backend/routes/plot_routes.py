"""Quick-select markers for the map default view."""

from __future__ import annotations

from fastapi import APIRouter

from config.geo_reference_points import GEO_REFERENCE_POINTS

router = APIRouter(prefix="/api/v1", tags=["plots"])


@router.get("/plots")
def get_plots():
    """Quick-select starting markers — not the only clickable locations."""
    return [
        {
            "locality": p["locality"],
            "longitude": p["longitude"],
            "latitude": p["latitude"],
            "geojson_position": [p["longitude"], p["latitude"]],
        }
        for p in GEO_REFERENCE_POINTS
    ]
