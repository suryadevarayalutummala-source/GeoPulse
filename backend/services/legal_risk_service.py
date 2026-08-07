"""
Legal & environmental risk flags for a map click (lon, lat).

Hackathon note: distance-to-OSM-water + GO 111 haversine are demo heuristics.
Production replacement: official HYDRAA FTL cadastral layers + notified GO 111
GIS polygons from Telangana / HMDA, not OpenStreetMap approximations.
"""

from __future__ import annotations

import math
from typing import Any

from config.rules_config import HYDERABAD_REGULATORY_RULES

_EARTH_RADIUS_M = 6371000.0


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(a)))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return _haversine_m(lat1, lon1, lat2, lon2) / 1000.0


def _point_to_ring_min_m(lat: float, lon: float, ring: list[list[float]]) -> float | None:
    """Min distance from point to GeoJSON-ish ring of [lon, lat] positions."""
    if not ring:
        return None
    best = float("inf")
    for pos in ring:
        if not isinstance(pos, (list, tuple)) or len(pos) < 2:
            continue
        plon, plat = float(pos[0]), float(pos[1])
        best = min(best, _haversine_m(lat, lon, plat, plon))
    return None if best == float("inf") else best


def _water_body_distance_m(lat: float, lon: float, body: dict[str, Any]) -> float | None:
    """Prefer geometry rings; fall back to a single centroid lat/lon."""
    geom = body.get("geometry") or body.get("coordinates")
    if isinstance(geom, list) and geom:
        # Polygon: list of rings, or flat ring of [lon,lat]
        if geom and isinstance(geom[0], (list, tuple)) and len(geom[0]) == 2 and not isinstance(
            geom[0][0], (list, tuple)
        ):
            return _point_to_ring_min_m(lat, lon, geom)
        # Multi-ring / polygon exterior
        if geom and isinstance(geom[0], list):
            ring = geom[0] if geom and isinstance(geom[0][0], (list, tuple)) else geom
            return _point_to_ring_min_m(lat, lon, ring)

    blat = body.get("lat")
    blon = body.get("lon")
    if blat is not None and blon is not None:
        return _haversine_m(lat, lon, float(blat), float(blon))
    return None


def _is_major_water(body: dict[str, Any]) -> bool:
    """Heuristic: named lakes / reservoirs / large OSM water → 30m buffer; else 9m."""
    name = (body.get("name") or "").lower()
    water = (body.get("water") or body.get("waterway") or "").lower()
    tags = body.get("tags") or {}
    if isinstance(tags, dict):
        name = name or (tags.get("name") or "").lower()
        water = water or (tags.get("water") or tags.get("waterway") or "").lower()
    major_tokens = ("lake", "sagar", "reservoir", "cheruvu", "tank")
    if any(t in name for t in major_tokens) or water in ("lake", "reservoir"):
        return True
    # Area hint if Overpass provided
    area = body.get("area_sq_m")
    try:
        if area is not None and float(area) >= 100_000:  # ~10 hectares
            return True
    except (TypeError, ValueError):
        pass
    return False


def evaluate_legal_and_environmental_risks(
    lon: float,
    lat: float,
    locality: str,
    nearby_water_bodies: list,
) -> dict[str, Any]:
    rules = HYDERABAD_REGULATORY_RULES
    flags: list[dict[str, Any]] = []
    map_buffers: list[dict[str, Any]] = []

    major_m = float(rules["LAKE_BUFFER_MAJOR_METERS"])
    minor_m = float(rules["LAKE_BUFFER_MINOR_METERS"])
    hist_m = float(rules.get("HISTORICAL_LAKE_BUFFER_MAJOR_METERS", 9.0))
    curr_m = float(rules.get("CURRENT_LAKE_BUFFER_MAJOR_METERS", major_m))

    for body in nearby_water_bodies or []:
        dist = _water_body_distance_m(lat, lon, body)
        if dist is None:
            continue
        is_major = _is_major_water(body)
        threshold = major_m if is_major else minor_m
        name = body.get("name") or (body.get("tags") or {}).get("name") or "unnamed water body"

        # Map overlay hint for frontend (30m red buffer around water centroid if known)
        blat = body.get("lat")
        blon = body.get("lon")
        if blat is not None and blon is not None:
            map_buffers.append(
                {
                    "center": [float(blon), float(blat)],  # GeoJSON [lon, lat]
                    "radius_m": threshold,
                    "name": name,
                }
            )

        if dist < threshold:
            code = "HYDRAA_FTL_BUFFER"
            severity = "CRITICAL"
            flags.append(
                {
                    "code": code,
                    "severity": severity,
                    "description": (
                        f"Property is {dist:.0f}m from notified lake/nala boundary "
                        f"'{name}' (min {threshold:.0f}m required). "
                        "Violates HYDRAA FTL Buffer Zone. High risk of demolition/encroachment flags."
                    ),
                    "distance_m": round(dist, 1),
                    "required_buffer_m": threshold,
                    "water_body": name,
                }
            )

        # Retroactive: legal under old 9m rule, illegal under current 30m
        if is_major and hist_m <= dist < curr_m:
            flags.append(
                {
                    "code": "RETROACTIVE_BUFFER_TIGHTENING",
                    "severity": "WARNING",
                    "description": (
                        f"Distance to '{name}' is {dist:.0f}m — may have been compliant under the "
                        f"historical {hist_m:.0f}m buffer but is non-compliant under the current "
                        f"{curr_m:.0f}m HYDRAA FTL rule (retroactive enforcement risk)."
                    ),
                    "distance_m": round(dist, 1),
                    "historical_buffer_m": hist_m,
                    "current_buffer_m": curr_m,
                    "water_body": name,
                }
            )

    # GO 111 catchment (Osman Sagar / Himayat Sagar)
    go_radius = float(rules["GO_111_RADIUS_KM"])
    for lake in rules.get("GO_111_LAKES") or []:
        d_km = _haversine_km(lat, lon, float(lake["lat"]), float(lake["lon"]))
        if d_km < go_radius:
            flags.append(
                {
                    "code": "GO_111_CATCHMENT",
                    "severity": "WARNING",
                    "description": (
                        f"Located within GO 111 Catchment Protection Zone "
                        f"({d_km:.1f} km from {lake['name']}; radius {go_radius:.0f} km). "
                        "Residential construction strictly restricted."
                    ),
                    "distance_km": round(d_km, 2),
                    "lake": lake["name"],
                }
            )

    # Active HYDRAA drive locality
    locality_l = (locality or "").lower()
    for zone in rules.get("ACTIVE_HYDRAA_DRIVE_ZONES") or []:
        if zone.lower() in locality_l:
            flags.append(
                {
                    "code": "HYDRAA_DRIVE_ZONE",
                    "severity": "WARNING",
                    "description": (
                        f"Locality matches active HYDRAA enforcement-drive zone '{zone}'. "
                        "Expect heightened scrutiny of layout / LRS / encroachment status."
                    ),
                    "zone": zone,
                }
            )
            break

    has_critical = any(f["severity"] == "CRITICAL" for f in flags)
    has_warning = any(f["severity"] == "WARNING" for f in flags)

    if has_critical:
        risk_level = "HIGH"
        marker = "red"
    elif has_warning:
        risk_level = "CAUTION"
        marker = "yellow"
    else:
        risk_level = "SAFE"
        marker = "green"
        flags.append(
            {
                "code": "NO_REGULATORY_HIT",
                "severity": "SAFE",
                "description": (
                    "No HYDRAA FTL buffer, GO 111 catchment, or active-drive-zone hit "
                    "in available demo data. Not a substitute for title / HYDRAA verification."
                ),
            }
        )

    return {
        "risk_level": risk_level,
        "marker_color": marker,
        "flags": flags,
        "map_buffers": map_buffers,
    }
