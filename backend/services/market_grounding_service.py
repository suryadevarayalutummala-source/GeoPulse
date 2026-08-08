"""
Live market + legal/news RAG via Gemini Google Search grounding.

Hackathon note: grounding is directional for demos.
Production replacement: licensed comps / HMDA notice feeds.
Spatial cache key: round(lat, 3):round(lon, 3).
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"

# Shared with ai_fallback_service consumers — keyed by rounded lon/lat
market_spatial_cache: dict[str, dict[str, Any]] = {}

_FALLBACK_MARKET = {
    "avg_price_sqft": "Data unavailable",
    "rental_yield": "N/A",
    "growth_trend": "Unknown",
    "legal_notices": [],
    "found_reliable_data": False,
    "source_note": "Fallback — grounding unavailable",
}


def spatial_cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 3)}:{round(lon, 3)}"


def _parse_json_object(text: str) -> dict[str, Any] | None:
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def get_live_market_context(
    locality: str | None,
    *,
    lat: float,
    lon: float,
) -> dict[str, Any]:
    """Grounded market dict; always returns a dict (fallback on failure)."""
    key = spatial_cache_key(lat, lon)
    if key in market_spatial_cache:
        return market_spatial_cache[key]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return dict(_FALLBACK_MARKET)

    place = locality or f"lon {lon:.4f}, lat {lat:.4f}"
    prompt = f"""
You are researching residential real-estate near {place}
(Hyderabad, India; lon={lon}, lat={lat}).

Use Google Search grounding. Return ONLY JSON:
{{
  "avg_price_sqft": "₹X - ₹Y or a single figure string",
  "rental_yield": "e.g. 3.8%",
  "growth_trend": "High|Moderate|Low|Unknown",
  "current_price_sqft": number or null,
  "rental_yield_percent": number or null,
  "legal_notices": ["short strings about HMDA layout approvals, LRS updates, or legal notices if any"],
  "found_reliable_data": true/false,
  "source_note": "short caveat"
}}
If nothing reliable, found_reliable_data=false and use nulls / empty lists.
No markdown.
""".strip()

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
            ),
        )
        parsed = _parse_json_object(response.text or "")
        if not parsed or parsed.get("found_reliable_data") is False:
            result = dict(_FALLBACK_MARKET)
            if parsed:
                result["source_note"] = parsed.get("source_note") or result["source_note"]
                result["legal_notices"] = parsed.get("legal_notices") or []
            market_spatial_cache[key] = result
            return result

        price_num = parsed.get("current_price_sqft")
        result = {
            "avg_price_sqft": parsed.get("avg_price_sqft")
            or (f"₹{int(price_num):,}" if price_num else "Data unavailable"),
            "rental_yield": parsed.get("rental_yield")
            or (
                f"{parsed.get('rental_yield_percent')}%"
                if parsed.get("rental_yield_percent") is not None
                else "N/A"
            ),
            "growth_trend": parsed.get("growth_trend") or "Unknown",
            "current_price_sqft": float(price_num) if price_num is not None else None,
            "rental_yield_percent": (
                float(parsed["rental_yield_percent"])
                if parsed.get("rental_yield_percent") is not None
                else None
            ),
            "legal_notices": parsed.get("legal_notices") or [],
            "found_reliable_data": True,
            "source_note": parsed.get("source_note") or "Gemini Google Search grounding",
            # legacy aliases for location_context_service
            "price_per_sqft": float(price_num) if price_num is not None else 0,
            "roi_index": 0,
            "historical_growth_percent": 0,
            "future_growth_percent": 0,
        }
        market_spatial_cache[key] = result
        return result
    except Exception:
        logger.exception("Market grounding failed for %s", key)
        return dict(_FALLBACK_MARKET)


# Back-compat wrapper used by location_context_service (named longitude/latitude)
def get_live_market_context_compat(
    locality_name: str | None,
    *,
    longitude: float,
    latitude: float,
) -> dict[str, Any] | None:
    result = get_live_market_context(locality_name, lat=latitude, lon=longitude)
    if not result.get("found_reliable_data"):
        return None
    return result
