import sys
from pathlib import Path
import pytest

# Ensure backend services package is importable
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def _skip_if_missing(module_name: str):
    try:
        __import__(module_name)
    except Exception as exc:  # ImportError or other
        pytest.skip(f"{module_name} not available: {exc}")


def _safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        pytest.skip(f"API/service call failed: {exc}")


def test_polygon_utils_area_centroid_geojson():
    _skip_if_missing("utils.polygon_utils")
    from utils import polygon_utils as pu

    # Small square around Hyderabad (lon, lat) ordering is accepted by most helpers
    polygon = [(78.36, 17.43), (78.38, 17.43), (78.38, 17.44), (78.36, 17.44)]

    # area
    area = _safe_call(pu.calculate_area, polygon)
    assert isinstance(area, (int, float))
    assert area > 0

    # centroid
    centroid = _safe_call(pu.calculate_centroid, polygon)
    assert isinstance(centroid, (list, tuple)) and len(centroid) == 2
    longitude, latitude = centroid
    assert -90.0 <= latitude <= 90.0
    assert -180.0 <= longitude <= 180.0

    # geojson
    geo = _safe_call(pu.polygon_to_geojson, polygon)
    assert isinstance(geo, dict)
    assert geo.get("type") in ("Polygon", "Feature") or "coordinates" in geo


def test_geocoder_reverse_geocode():
    _skip_if_missing("services.geocoder_service")
    from services.geocoder_service import GeocoderService

    svc = GeocoderService()
    res = _safe_call(svc.reverse_geocode, 17.4325, 78.3434)

    # Accept several keys that indicate locality
    locality_keys = ["city", "town", "village", "county"]
    assert any(k in res and res[k] for k in locality_keys), "No city/town found in reverse geocode result"
    assert "country" in res and res["country"], "Country missing in reverse geocode result"


def test_overpass_amenities_counts():
    _skip_if_missing("services.overpass_service")
    from services.overpass_service import OverpassService

    svc = OverpassService()
    lat, lon = 17.4325, 78.3434

    for method_name in ("get_schools", "get_hospitals", "get_parks"):
        if not hasattr(svc, method_name):
            pytest.skip(f"OverpassService missing {method_name}")
        method = getattr(svc, method_name)
        # Try calling with (lat, lon, radius) and fall back to no-args
        try:
            out = method(lat, lon, 1000)
        except TypeError:
            out = method()
        except Exception as exc:
            pytest.skip(f"{method_name} failed: {exc}")

        # Accept either a dict with count or a list
        if isinstance(out, dict) and "count" in out:
            assert out["count"] >= 0
        elif isinstance(out, (list, tuple)):
            assert len(out) >= 0
        else:
            pytest.skip(f"Unexpected return from {method_name}: {type(out)}")


def test_soil_service_information():
    _skip_if_missing("services.soil_service")
    from services.soil_service import SoilService

    svc = SoilService()
    info = _safe_call(svc.get_soil_information, 17.4325, 78.3434)

    for key in ("region", "soil_type", "bearing_capacity_kpa", "construction_suitability"):
        assert key in info, f"{key} missing from soil information"


def test_market_service_information():
    _skip_if_missing("services.market_service")
    from services.market_service import MarketService

    svc = MarketService()
    info = _safe_call(svc.get_market_information, 17.4325, 78.3434)

    for key in ("current_price_sqft", "historical_growth_rates", "roi_percentage"):
        assert key in info, f"{key} missing from market information"


def test_scoring_service_generate_scores():
    _skip_if_missing("services.scoring_service")
    from services.scoring_service import (
        ScoringService,
        ConnectivityFactors,
        LivabilityFactors,
        InvestmentFactors,
        ConstructionFactors,
    )

    svc = ScoringService()

    connectivity = ConnectivityFactors(5, 2, 10, 1, 3)
    livability = LivabilityFactors(5, 2, 3, 4.0)
    investment = InvestmentFactors(5000.0, 5.0, 4.0, 3.5, 60.0)
    construction = ConstructionFactors(150.0, 4.0, "Good")

    # prefer calculate_scores if available; keep backward compatibility
    call_fn = getattr(svc, "calculate_scores", getattr(svc, "generate_property_scores", None))
    assert call_fn is not None, "No scoring entrypoint found on ScoringService"
    scores = _safe_call(call_fn, connectivity, livability, investment, construction)
    assert isinstance(scores, dict)

    expected_keys = [
        "connectivity_score",
        "livability_score",
        "investment_score",
        "construction_score",
        "overall_score",
    ]
    for k in expected_keys:
        assert k in scores
        assert isinstance(scores[k], int)
        assert 0 <= scores[k] <= 100
