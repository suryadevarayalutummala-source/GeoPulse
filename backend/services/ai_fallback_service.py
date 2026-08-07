"""Three-layer AI fallback: live Gemini → in-memory cache → static copy."""

from __future__ import annotations

import logging
from typing import Any

from services.ai_prompt_service import normalize_role
from services.gemini_client import call_gemini_for_chat, call_gemini_for_summary
from services.location_context_service import round_coord_key
from services.market_grounding_service import (
    get_live_market_context,
    market_spatial_cache,
    spatial_cache_key,
)

logger = logging.getLogger(__name__)

cache: dict[str, Any] = {}

# Re-export spatial market cache (keyed round(lat,3):round(lon,3) in market_grounding_service)
__all__ = [
    "cache",
    "market_spatial_cache",
    "spatial_cache_key",
    "get_market_context_cached",
    "get_static_fallback",
    "get_ai_summary_safe",
    "get_ai_chat_safe",
]


def get_market_context_cached(
    locality: str | None,
    *,
    lat: float,
    lon: float,
) -> dict[str, Any]:
    """Cached Gemini grounding with built-in fallback defaults."""
    return get_live_market_context(locality, lat=lat, lon=lon)

# Single editable block for static demo fallbacks — replace later without hunting inline strings.
_STATIC_FALLBACKS: dict[str, dict[str, list[str]]] = {
    "builder": {
        "summary_points": [
            "Confirm bearing capacity and water-table depth with a site-specific geotech bore log before foundation design.",
            "Hyderabad Deccan basalt / residual red soils often support mid-rise loads; lake-adjacent and filled historic pockets need extra caution.",
            "Treat construction_score plus flood/zoning notes as your primary construction-risk signals for this click.",
        ],
        "suggested_questions": [
            "What foundation type fits this point's interpolated bearing capacity and water-table depth?",
            "Does the construction_score suggest dewatering or excavation risk here?",
            "What geotechnical tests should a builder order before breaking ground in Hyderabad?",
        ],
    },
    "investor": {
        "summary_points": [
            "IT and peri-urban Hyderabad corridors typically show stronger forward growth than older core residential pockets.",
            "Cross-check current_price_sqft against rental_yield_percentage and roi_percentage before underwriting.",
            "Use risk_score together with investment_score when comparing locations side by side.",
        ],
        "suggested_questions": [
            "How does rental_yield_percentage compare with historical_growth_rates here?",
            "Is the risk_score acceptable given current_price_sqft?",
            "What hold period do investors typically underwrite for Hyderabad residential land?",
        ],
    },
    "homebuyer": {
        "summary_points": [
            "Daily convenience hinges more on nearest_hospital_km than raw amenity counts.",
            "Connectivity_score reflects transit_hubs_nearby — critical for commute-heavy Hyderabad households.",
            "Balance livability_score with budget when comparing suburbs.",
        ],
        "suggested_questions": [
            "How far is nearest_hospital_km from this map click?",
            "Do schools_nearby and hospitals_nearby look sufficient for a family?",
            "What should homebuyers prioritize when comparing Hyderabad suburbs?",
        ],
    },
}

_CHAT_FALLBACK = (
    "I'm unable to reach the AI advisor right now. Please try again in a moment, "
    "or use the role summary cards while connectivity is restored."
)


def get_static_fallback(role: str) -> dict[str, list[str]]:
    role = normalize_role(role)
    return _STATIC_FALLBACKS.get(role, _STATIC_FALLBACKS["investor"])


def get_ai_summary_safe(
    *,
    longitude: float,
    latitude: float,
    role: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    role = normalize_role(role)
    cache_key = f"{round_coord_key(longitude, latitude)}:{role}"
    try:
        result = call_gemini_for_summary(role, context)
        cache[cache_key] = result
        return result
    except Exception:
        logger.exception("Gemini summary failed for %s", cache_key)
        if cache_key in cache:
            return cache[cache_key]
        return get_static_fallback(role)


def get_ai_chat_safe(
    *,
    longitude: float,
    latitude: float,
    role: str,
    context: dict[str, Any],
    message: str,
    conversation_history: list[dict] | None = None,
) -> str:
    role = normalize_role(role)
    cache_key = f"{round_coord_key(longitude, latitude)}:{role}:{message.strip().lower()}"
    try:
        answer = call_gemini_for_chat(role, context, message, conversation_history)
        cache[cache_key] = answer
        return answer
    except Exception:
        logger.exception("Gemini chat failed for %s", cache_key)
        if cache_key in cache:
            return cache[cache_key]
        return _CHAT_FALLBACK
