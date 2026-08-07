"""
Demo soil estimation via inverse-distance-weighted interpolation (p=2).

Hackathon note: values come from config/geo_reference_points.py (ESTIMATED_DEMO_VALUES).
Production replacement: certified geotechnical borehole / licensed soil GIS API.
"""

from __future__ import annotations

import math
from typing import Any

from config.geo_reference_points import GEO_REFERENCE_POINTS

_EARTH_RADIUS_KM = 6371.0
_IDW_POWER = 2
_ESTIMATION_NOTE = (
    "Interpolated from regional geological reference data — informational estimate, "
    "not a certified geotechnical survey"
)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def estimate_soil_properties(*, longitude: float, latitude: float) -> dict[str, Any]:
    """IDW (p=2) over all reference points; soil_type from nearest neighbor."""
    ranked: list[tuple[float, dict]] = []
    for point in GEO_REFERENCE_POINTS:
        dist = _haversine_km(latitude, longitude, point["latitude"], point["longitude"])
        ranked.append((dist, point))
    ranked.sort(key=lambda item: item[0])
    nearest = ranked[0][1] if ranked else {}

    if ranked and ranked[0][0] < 0.05:
        return {
            "bearing_capacity_kpa": float(nearest["bearing_capacity_kpa"]),
            "water_table_depth_m": float(nearest["water_table_depth_m"]),
            "soil_type": nearest.get("soil_type") or "Unknown",
            "estimation_note": _ESTIMATION_NOTE,
            "nearest_locality": nearest.get("locality"),
        }

    weight_sum = 0.0
    bearing_acc = 0.0
    water_acc = 0.0
    for dist_km, point in ranked:
        w = 1.0 / ((dist_km + 1e-6) ** _IDW_POWER)
        weight_sum += w
        bearing_acc += w * float(point["bearing_capacity_kpa"])
        water_acc += w * float(point["water_table_depth_m"])

    return {
        "bearing_capacity_kpa": round(bearing_acc / weight_sum, 1),
        "water_table_depth_m": round(water_acc / weight_sum, 2),
        "soil_type": nearest.get("soil_type") or "Red Sandy Loam",
        "estimation_note": _ESTIMATION_NOTE,
        "nearest_locality": nearest.get("locality"),
    }
