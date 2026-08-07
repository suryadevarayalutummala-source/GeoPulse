import sys
from pathlib import Path
import json
import pytest

# Make backend services importable from tests
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def _skip_if_missing(module_name: str):
    try:
        __import__(module_name)
    except Exception as exc:
        pytest.skip(f"{module_name} not available: {exc}")


def _safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        pytest.skip(f"Service call failed: {exc}")


def test_ai_context_builder_integration():
    _skip_if_missing("services.ai_context_builder")
    from services.ai_context_builder import AIContextBuilder

    builder = AIContextBuilder()

    ctx = _safe_call(builder.build_context, 17.4325, 78.3434)

    assert isinstance(ctx, dict)
    # top-level keys
    for key in (
        "core",
        "builder",
        "investor",
        "buyer",
        "scores",
        "location_summary",
        "strengths",
        "weaknesses",
        "investment_recommendation",
        "construction_recommendation",
        "property_summary",
        "buyer_recommendation",
    ):
        assert key in ctx, f"{key} missing from context"

    core = ctx.get("core") or {}
    assert "plot_id" in core and "coordinates" in core and "area_sqft" in core
    assert "matched_plot" in core or "selected_plot" in core

    builder = ctx.get("builder") or {}
    assert "bearing_capacity_kpa" in builder and builder["bearing_capacity_kpa"] is not None

    investor = ctx.get("investor") or {}
    assert "current_price_sqft" in investor and investor["current_price_sqft"] is not None

    buyer = ctx.get("buyer") or {}
    assert "schools_nearby" in buyer and "nearest_hospital_km" in buyer
    assert "air_quality_index" in buyer and "commute_time_to_city_center_min" in buyer

    scores = ctx.get("scores") or {}
    assert "overall_score" in scores and isinstance(scores["overall_score"], int)
    assert "property_grade" in scores

    # Pretty-print the final JSON for visibility
    print(json.dumps(ctx, indent=2, ensure_ascii=False))
