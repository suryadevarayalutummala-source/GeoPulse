"""
Assemble full location context for ANY Hyderabad lon/lat click.

Team schema (source of truth from data teammate):
  core / builder / investor / buyer / scores

Pipeline:
1. AIContextBuilder.build_context(longitude=..., latitude=...)
2. Ensure core/builder/investor/buyer/scores buckets exist
3. Overlay IDW soil estimates onto builder.* when missing/zero
4. Overlay grounded market data onto investor.* when available
5. Cache by rounded lon/lat
"""

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any

from services.ai_context_builder import AIContextBuilder
from services.market_grounding_service import get_live_market_context_compat
from services.soil_interpolation_service import estimate_soil_properties

logger = logging.getLogger(__name__)

_assembled_cache: dict[str, dict[str, Any]] = {}

_EMPTY_CORE = {
    "plot_id": None,
    "name": "",
    "coordinates": {"longitude": None, "latitude": None},
    "area_sqft": 0,
    "zoning_type": "",
    "ownership_status": "",
    "plot_boundary_geojson": {},
}

_EMPTY_BUILDER = {
    "bearing_capacity_kpa": 0,
    "water_table_depth_m": 0,
    "soil_type": "",
    "flood_risk_zone": "",
    "max_permissible_floors": 0,
    "utility_access": "",
    "construction_cost_estimate_per_sqft": 0,
}

_EMPTY_INVESTOR = {
    "current_price_sqft": 0,
    "historical_growth_rates": [],
    "rental_yield_percentage": 0,
    "roi_percentage": 0,
    "risk_score": 0,
    "infrastructure_development_pipeline": [],
}

_EMPTY_BUYER = {
    "schools_nearby": 0,
    "hospitals_nearby": 0,
    "transit_hubs_nearby": 0,
    "nearest_hospital_km": 0,
    "air_quality_index": 0,
    "commute_time_to_city_center_min": 0,
}

_EMPTY_SCORES = {
    "connectivity_score": 0,
    "livability_score": 0,
    "investment_score": 0,
    "construction_score": 0,
    "overall_score": 0,
}


def round_coord_key(longitude: float, latitude: float) -> str:
    """Cache key uses lon,lat order (team / GeoJSON convention)."""
    return f"{round(longitude, 2)}:{round(latitude, 2)}"


def _is_placeholder_number(value: Any) -> bool:
    try:
        return value is None or float(value) == 0.0
    except (TypeError, ValueError):
        return True


def _merge_defaults(base: dict[str, Any], incoming: dict[str, Any] | None) -> dict[str, Any]:
    out = deepcopy(base)
    if not incoming:
        return out
    for key, value in incoming.items():
        out[key] = value
    return out


def normalize_context(
    raw: dict[str, Any],
    *,
    longitude: float,
    latitude: float,
) -> dict[str, Any]:
    """
    Normalize to finalized team buckets only:
    core, builder, investor, buyer, scores.
    """
    raw = raw if isinstance(raw, dict) else {}

    # Already in finalized shape
    if any(k in raw for k in ("core", "builder", "investor", "buyer")):
        core = _merge_defaults(_EMPTY_CORE, raw.get("core"))
        builder = _merge_defaults(_EMPTY_BUILDER, raw.get("builder"))
        investor = _merge_defaults(_EMPTY_INVESTOR, raw.get("investor"))
        buyer = _merge_defaults(_EMPTY_BUYER, raw.get("buyer"))
        scores = _merge_defaults(_EMPTY_SCORES, raw.get("scores"))
    else:
        # Legacy location/soil/market/amenities → map into team field names
        location = raw.get("location") or {}
        polygon = raw.get("polygon") or {}
        soil = raw.get("soil") or {}
        market = raw.get("market") or {}
        amenities = raw.get("amenities") or {}
        scores = _merge_defaults(_EMPTY_SCORES, raw.get("scores"))
        centroid = polygon.get("centroid") or []

        core = _merge_defaults(
            _EMPTY_CORE,
            {
                "plot_id": location.get("plot_id"),
                "name": location.get("name") or location.get("city") or "",
                "coordinates": {
                    "longitude": (location.get("coordinates") or {}).get("longitude")
                    if isinstance(location.get("coordinates"), dict)
                    else (centroid[0] if len(centroid) > 0 else longitude),
                    "latitude": (location.get("coordinates") or {}).get("latitude")
                    if isinstance(location.get("coordinates"), dict)
                    else (centroid[1] if len(centroid) > 1 else latitude),
                },
                "area_sqft": location.get("area_sqft")
                or round(float(polygon.get("area_sq_m") or 0) / 0.092903, 2),
                "zoning_type": location.get("zoning_type") or soil.get("region") or "",
                "ownership_status": location.get("ownership_status") or "",
                "plot_boundary_geojson": polygon.get("plot_boundary_geojson") or {},
            },
        )
        builder = _merge_defaults(
            _EMPTY_BUILDER,
            {
                "bearing_capacity_kpa": soil.get("bearing_capacity_kpa") or 0,
                "water_table_depth_m": soil.get("water_table_depth_m") or 0,
                "soil_type": soil.get("soil_type") or "",
                "flood_risk_zone": soil.get("flood_risk_zone") or "",
                "max_permissible_floors": soil.get("max_permissible_floors") or 0,
                "utility_access": soil.get("construction_suitability")
                or soil.get("utility_access")
                or "",
                "construction_cost_estimate_per_sqft": soil.get(
                    "construction_cost_estimate_per_sqft"
                )
                or 0,
            },
        )
        rates = market.get("historical_growth_rates")
        if not rates and market.get("historical_growth_percent") is not None:
            rates = [market.get("historical_growth_percent")]
        investor = _merge_defaults(
            _EMPTY_INVESTOR,
            {
                "current_price_sqft": market.get("current_price_sqft")
                or market.get("price_per_sqft")
                or 0,
                "historical_growth_rates": rates or [],
                "rental_yield_percentage": market.get("rental_yield_percentage")
                or market.get("rental_yield_percent")
                or 0,
                "roi_percentage": market.get("roi_percentage")
                or market.get("roi_index")
                or 0,
                "risk_score": market.get("risk_score") or 0,
                "infrastructure_development_pipeline": market.get(
                    "infrastructure_development_pipeline"
                )
                or [],
            },
        )
        buyer = _merge_defaults(
            _EMPTY_BUYER,
            {
                "schools_nearby": amenities.get("schools_nearby")
                or amenities.get("schools")
                or 0,
                "hospitals_nearby": amenities.get("hospitals_nearby")
                or amenities.get("hospitals")
                or 0,
                "transit_hubs_nearby": amenities.get("transit_hubs_nearby")
                or amenities.get("metro")
                or 0,
                "nearest_hospital_km": amenities.get("nearest_hospital_km") or 0,
                "air_quality_index": amenities.get("air_quality_index") or 0,
                "commute_time_to_city_center_min": amenities.get(
                    "commute_time_to_city_center_min"
                )
                or 0,
            },
        )

    # Always stamp clicked coordinates (lon, lat named object)
    coords = core.get("coordinates") if isinstance(core.get("coordinates"), dict) else {}
    core["coordinates"] = {
        "longitude": coords.get("longitude") if coords.get("longitude") is not None else longitude,
        "latitude": coords.get("latitude") if coords.get("latitude") is not None else latitude,
    }

    return {
        "core": core,
        "builder": builder,
        "investor": investor,
        "buyer": buyer,
        "scores": scores,
    }


def assemble_location_context(
    longitude: float,
    latitude: float,
    locality_name: str | None = None,
    *,
    use_cache: bool = True,
) -> dict[str, Any]:
    key = round_coord_key(longitude, latitude)
    if use_cache and key in _assembled_cache:
        return deepcopy(_assembled_cache[key])

    try:
        raw = AIContextBuilder().build_context(longitude=longitude, latitude=latitude)
    except NotImplementedError:
        logger.warning("AIContextBuilder not implemented yet — using empty base context")
        raw = {}
    except Exception:
        logger.exception("AIContextBuilder failed — continuing with soil/market overlays")
        raw = {}

    ctx = normalize_context(
        raw if isinstance(raw, dict) else {},
        longitude=longitude,
        latitude=latitude,
    )

    builder = ctx["builder"]
    soil_est = estimate_soil_properties(longitude=longitude, latitude=latitude)
    if _is_placeholder_number(builder.get("bearing_capacity_kpa")):
        builder["bearing_capacity_kpa"] = soil_est["bearing_capacity_kpa"]
    if _is_placeholder_number(builder.get("water_table_depth_m")):
        builder["water_table_depth_m"] = soil_est["water_table_depth_m"]
    builder["estimation_note"] = soil_est.get("estimation_note")
    if not locality_name:
        locality_name = soil_est.get("nearest_locality")

    investor = ctx["investor"]
    live_market = get_live_market_context_compat(
        locality_name, longitude=longitude, latitude=latitude
    )
    if live_market:
        if live_market.get("price_per_sqft") is not None:
            investor["current_price_sqft"] = live_market["price_per_sqft"]
        if live_market.get("rental_yield_percent") is not None:
            investor["rental_yield_percentage"] = live_market["rental_yield_percent"]
        if live_market.get("roi_index") is not None:
            investor["roi_percentage"] = live_market["roi_index"]
        growth = []
        if live_market.get("historical_growth_percent") is not None:
            growth.append(live_market["historical_growth_percent"])
        if live_market.get("future_growth_percent") is not None:
            growth.append(live_market["future_growth_percent"])
        if growth:
            investor["historical_growth_rates"] = growth
        if live_market.get("source_note"):
            investor["market_source_note"] = live_market["source_note"]

    if locality_name and not ctx["core"].get("name"):
        ctx["core"]["name"] = locality_name

    ctx["locality_name"] = locality_name
    # Mapbox / GeoJSON: [longitude, latitude]
    ctx["geojson_position"] = [longitude, latitude]

    _assembled_cache[key] = deepcopy(ctx)
    return deepcopy(ctx)
