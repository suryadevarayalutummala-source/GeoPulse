from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .geocoder_service import GeocoderService, GeocoderServiceError
from .market_service import MarketService, MarketServiceError
from .overpass_service import OverpassService, OverpassServiceError
from .scoring_service import (
    ConstructionFactors,
    ConnectivityFactors,
    InvestmentFactors,
    LivabilityFactors,
    ScoringService,
    ScoringServiceError,
)
from .soil_service import SoilService, SoilServiceError
from .weather_service import WeatherService, WeatherServiceError
from .mapbox_service import MapboxService, MapboxServiceError

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

Coordinate = Tuple[float, float]
SearchRadius = int


class AIContextBuilderError(Exception):
    """Base exception raised by the AI context builder."""


class AIContextBuilder:
    DEFAULT_AMENITY_RADIUS: SearchRadius = 1000
    PLOTS_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "plots_final.json"

    def __init__(
        self,
        geocoder_service: Optional[GeocoderService] = None,
        overpass_service: Optional[OverpassService] = None,
        soil_service: Optional[SoilService] = None,
        market_service: Optional[MarketService] = None,
        scoring_service: Optional[ScoringService] = None,
        weather_service: Optional[WeatherService] = None,
        mapbox_service: Optional[MapboxService] = None,
    ) -> None:
        self.geocoder_service = geocoder_service or GeocoderService()
        self.overpass_service = overpass_service or OverpassService()
        self.soil_service = soil_service or SoilService()
        self.market_service = market_service or MarketService()
        self.scoring_service = scoring_service or ScoringService()
        self.weather_service = weather_service or WeatherService()
        self.mapbox_service = mapbox_service or MapboxService()

    def build_context(
        self,
        latitude: float,
        longitude: float,
        radius: SearchRadius = DEFAULT_AMENITY_RADIUS,
    ) -> Dict[str, Any]:
        """Build a single JSON-ready context payload for the provided coordinates."""
        self._validate_coordinates(latitude, longitude)

        logger.info("Starting AI context build for (%s, %s) with radius=%s", latitude, longitude, radius)

        plot_data = self._load_plot_data(latitude, longitude)
        location = self._build_location(latitude, longitude)
        amenities = self._build_amenities(latitude, longitude, radius)
        soil = self._build_soil(latitude, longitude, plot_data)
        market = self._build_market(latitude, longitude, plot_data)
        environment = self._build_environment(latitude, longitude)
        commute = self._build_commute(latitude, longitude)
        core = self._build_core(latitude, longitude, soil, market, plot_data)
        builder = self._build_builder(soil, plot_data)
        investor = self._build_investor(market, plot_data)
        buyer = self._build_buyer(amenities, soil, market, environment, commute, plot_data)
        scores = self._build_scores(amenities, soil, market, environment, commute)

        location_summary = self._build_location_summary(location, soil, market, buyer)
        strengths = self._build_strengths(soil, market, buyer)
        weaknesses = self._build_weaknesses(soil, market, buyer)
        investment_recommendation = self._build_investment_recommendation(scores, market)
        construction_recommendation = self._build_construction_recommendation(soil, scores)
        property_summary = {
            "cluster": core.get("cluster") or (plot_data or {}).get("cluster") or "Unknown",
            "landmark": core.get("landmark") or (plot_data or {}).get("landmark") or "Unknown",
            "overall_score": scores.get("overall_score", 0),
            "plot_id": core.get("plot_id") or (plot_data or {}).get("plot_id"),
            "name": core.get("name") or (plot_data or {}).get("name") or "Unknown",
        }
        buyer_recommendation = (
            "This area looks strong for residential buyers seeking schools, hospitals, and transit access."
            if buyer.get("schools_nearby", 0) > 0 or buyer.get("hospitals_nearby", 0) > 0
            else "Validate buyer demand and amenity access before committing to the parcel."
        )

        context: Dict[str, Any] = {
            "core": core,
            "builder": builder,
            "investor": investor,
            "buyer": buyer,
            "scores": scores,
            "location_summary": location_summary,
            "property_summary": property_summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "investment_recommendation": investment_recommendation,
            "construction_recommendation": construction_recommendation,
            "buyer_recommendation": buyer_recommendation,
        }

        logger.info("AI context build completed for (%s, %s)", latitude, longitude)
        return context

    def _validate_coordinates(self, latitude: float, longitude: float) -> None:
        if not (-90.0 <= latitude <= 90.0):
            logger.error("Latitude out of range: %s", latitude)
            raise AIContextBuilderError("latitude must be between -90 and 90")
        if not (-180.0 <= longitude <= 180.0):
            logger.error("Longitude out of range: %s", longitude)
            raise AIContextBuilderError("longitude must be between -180 and 180")

    def _build_location(self, latitude: float, longitude: float) -> Dict[str, Any]:
        try:
            geocode = self.geocoder_service.reverse_geocode(latitude, longitude)
            location_payload = {
                "latitude": latitude,
                "longitude": longitude,
                "city": geocode.get("city") or geocode.get("locality"),
                "district": geocode.get("district"),
                "state": geocode.get("state"),
                "country": geocode.get("country"),
                "display_name": geocode.get("display_name"),
                "postcode": geocode.get("postcode"),
                "matched_locality": geocode.get("matched_locality"),
            }
            logger.info("Location section built: %s", location_payload)
            return location_payload
        except GeocoderServiceError as exc:
            logger.warning("Geocoder failed for (%s, %s): %s", latitude, longitude, exc)
            return {
                "latitude": latitude,
                "longitude": longitude,
                "city": "Unknown",
                "district": "Unknown",
                "state": "Unknown",
                "country": "Unknown",
                "display_name": "Unknown",
                "postcode": "Unknown",
                "matched_locality": None,
            }

    def _build_amenities(self, latitude: float, longitude: float, radius: SearchRadius) -> Dict[str, Any]:
        try:
            amenities = self.overpass_service.get_amenities(latitude, longitude, radius)
            if not isinstance(amenities, dict):
                raise OverpassServiceError("OverpassService.get_amenities returned invalid data")
            logger.info("Amenities section built for (%s, %s) with multi-query", latitude, longitude)
            return amenities
        except OverpassServiceError as exc:
            logger.warning("Multi-category Overpass query failed for (%s, %s): %s", latitude, longitude, exc)
            categories = [
                "schools",
                "hospitals",
                "parks",
                "bus_stops",
                "metro",
                "shopping_malls",
            ]
            fallback = {}
            for category in categories:
                fallback[category] = {
                    "count": 0,
                    "names": [],
                    "coordinates": [],
                    "nearest_distance_m": None,
                    "error": str(exc),
                }
            return fallback

    def _build_soil(self, latitude: float, longitude: float, plot_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            soil_payload = self.soil_service.get_soil_information(latitude, longitude)
            logger.info("Soil section built: %s", soil_payload)
            return soil_payload
        except SoilServiceError as exc:
            logger.warning("Soil lookup failed for (%s, %s): %s", latitude, longitude, exc)
            return {
                "region": "Unknown",
                "name": "Unknown",
                "soil_type": "Unknown",
                "bearing_capacity_kpa": 0.0,
                "water_table_depth_m": 0.0,
                "construction_suitability": "Unknown",
                "error": "Unable to load soil information for the provided location.",
            }

    def _build_market(self, latitude: float, longitude: float, plot_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            market_payload = self.market_service.get_market_information(latitude, longitude)
            logger.info("Market section built: %s", market_payload)
            return market_payload
        except MarketServiceError as exc:
            logger.warning("Market lookup failed for (%s, %s): %s", latitude, longitude, exc)
            return {
                "region": "Unknown",
                "name": "Unknown",
                "current_price_sqft": 0.0,
                "historical_growth_rates": [],
                "rental_yield_percentage": 0.0,
                "roi_percentage": 0.0,
                "risk_score": 0.0,
                "infrastructure_development_pipeline": [],
                "error": "Unable to load market information for the provided location.",
            }

    def _build_core(
        self,
        latitude: float,
        longitude: float,
        soil: Dict[str, Any],
        market: Dict[str, Any],
        plot_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plot_data = plot_data or self._load_plot_data(latitude, longitude)
        return {
            "plot_id": plot_data.get("plot_id", "UNKNOWN-PLOT"),
            "name": plot_data.get("name", "Unknown locality"),
            "cluster": plot_data.get("cluster") or "Unknown",
            "landmark": plot_data.get("landmark") or plot_data.get("name") or "Unknown",
            "matched_plot": {
                "plot_id": plot_data.get("plot_id"),
                "name": plot_data.get("name"),
            },
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "area_sqft": plot_data.get("area_sqft", 0),
            "zoning_type": plot_data.get("zoning_type", "Unknown"),
            "ownership_status": plot_data.get("ownership_status", "Unknown"),
            "soil_region": soil.get("region"),
            "market_region": market.get("region"),
        }

    def _build_builder(self, soil: Dict[str, Any], plot_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        plot_builder = (plot_data or {}).get("builder") or {}
        return {
            "soil_type": plot_builder.get("soil_type") or soil.get("soil_type"),
            "bearing_capacity_kpa": plot_builder.get("bearing_capacity_kpa") or soil.get("bearing_capacity_kpa"),
            "water_table_depth_m": plot_builder.get("water_table_depth_m") or soil.get("water_table_depth_m"),
            "flood_risk_zone": plot_builder.get("flood_risk_zone") or soil.get("flood_risk_zone"),
            "max_permissible_floors": plot_builder.get("max_permissible_floors") or soil.get("max_permissible_floors"),
            "utility_access": plot_builder.get("utility_access") or soil.get("utility_access"),
            "construction_cost_estimate_per_sqft": plot_builder.get("construction_cost_estimate_per_sqft") or soil.get("construction_cost_estimate_per_sqft"),
            "construction_suitability": plot_builder.get("construction_suitability") or soil.get("construction_suitability"),
            "foundation_recommendation": plot_builder.get("foundation_recommendation") or soil.get("foundation_recommendation"),
            "groundwater_risk": plot_builder.get("groundwater_risk") or soil.get("groundwater_risk"),
            "excavation_difficulty": plot_builder.get("excavation_difficulty") or soil.get("excavation_difficulty"),
        }

    def _build_investor(self, market: Dict[str, Any], plot_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        plot_investor = (plot_data or {}).get("investor") or {}
        return {
            "current_price_sqft": plot_investor.get("current_price_sqft") or market.get("current_price_sqft") or market.get("price_per_sqft"),
            "historical_growth_rates": plot_investor.get("historical_growth_rates") or market.get("historical_growth_rates") or [market.get("historical_growth_percent", 0.0)],
            "rental_yield_percentage": plot_investor.get("rental_yield_percentage") or market.get("rental_yield_percentage") or market.get("rental_yield_percent"),
            "roi_percentage": plot_investor.get("roi_percentage") or market.get("roi_percentage") or market.get("roi_index"),
            "risk_score": plot_investor.get("risk_score") or market.get("risk_score"),
            "infrastructure_development_pipeline": plot_investor.get("infrastructure_development_pipeline") or market.get("infrastructure_development_pipeline") or market.get("infrastructure_projects", []),
        }

    def _build_buyer(
        self,
        amenities: Dict[str, Any],
        soil: Dict[str, Any],
        market: Dict[str, Any],
        environment: Dict[str, Any],
        commute: Dict[str, Any],
        plot_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plot_buyer = (plot_data or {}).get("buyer") or {}
        schools_nearby = plot_buyer.get("schools_nearby")
        if schools_nearby is None:
            schools_nearby = self._safe_count(amenities.get("schools"))
        hospitals_nearby = plot_buyer.get("hospitals_nearby")
        if hospitals_nearby is None:
            hospitals_nearby = self._safe_count(amenities.get("hospitals"))
        transit_hubs_nearby = plot_buyer.get("transit_hubs_nearby")
        if transit_hubs_nearby is None:
            transit_hubs_nearby = self._safe_count(amenities.get("metro")) + self._safe_count(amenities.get("bus_stops"))
        nearest_hospital_km = plot_buyer.get("nearest_hospital_km")
        if nearest_hospital_km is None:
            nearest_hospital_km = self._nearest_distance_km(amenities.get("hospitals"))
        nearest_school_km = plot_buyer.get("nearest_school_km")
        if nearest_school_km is None:
            nearest_school_km = self._nearest_distance_km(amenities.get("schools"))
        return {
            "schools_nearby": schools_nearby,
            "hospitals_nearby": hospitals_nearby,
            "transit_hubs_nearby": transit_hubs_nearby,
            "nearest_hospital_km": nearest_hospital_km,
            "nearest_school_km": nearest_school_km,
            "top_nearby_schools": self._top_names(amenities.get("schools")) or plot_buyer.get("top_nearby_schools", []),
            "top_nearby_hospitals": self._top_names(amenities.get("hospitals")) or plot_buyer.get("top_nearby_hospitals", []),
            "top_nearby_shopping_centres": self._top_names(amenities.get("shopping_malls")) or plot_buyer.get("top_nearby_shopping_centres", []),
            "air_quality_index": plot_buyer.get("air_quality_index") if plot_buyer.get("air_quality_index") is not None else environment.get("air_quality_index"),
            "pm2_5": environment.get("pm2_5"),
            "pm10": environment.get("pm10"),
            "temperature_c": environment.get("temperature_c"),
            "humidity_percent": environment.get("humidity_percent"),
            "commute_time_to_city_center_min": plot_buyer.get("commute_time_to_city_center_min") if plot_buyer.get("commute_time_to_city_center_min") is not None else commute.get("commute_time_to_city_center_min"),
            "travel_time_to_airport": commute.get("travel_time_to_airport"),
            "travel_time_to_nearest_metro": commute.get("travel_time_to_nearest_metro"),
            "soil_suitability": soil.get("construction_suitability"),
            "market_trend": market.get("market_trend"),
        }

    def _load_plot_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        try:
            if not self.PLOTS_DATA_FILE.exists():
                raise FileNotFoundError(self.PLOTS_DATA_FILE)
            payload = json.loads(self.PLOTS_DATA_FILE.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ValueError("plots data must be a list")
            plot_records = [plot_data for plot_data in payload if isinstance(plot_data, dict)]
            if not plot_records:
                return {}

            try:
                geocode = self.geocoder_service.reverse_geocode(latitude, longitude)
                selected_plot = geocode.get("selected_plot")
                if isinstance(selected_plot, dict):
                    return selected_plot
            except Exception:
                pass

            best_plot = None
            best_distance = float("inf")
            for plot_data in plot_records:
                coords = plot_data.get("coordinates") or {}
                plot_latitude = coords.get("latitude")
                plot_longitude = coords.get("longitude")
                if plot_latitude is None or plot_longitude is None:
                    continue
                distance = self._haversine_distance(latitude, longitude, float(plot_latitude), float(plot_longitude))
                if distance < best_distance:
                    best_distance = distance
                    best_plot = plot_data
            return best_plot or plot_records[0]
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load plot metadata: %s", exc)
            return {}

    def _haversine_distance(self, latitude: float, longitude: float, target_latitude: float, target_longitude: float) -> float:
        radius_km = 6371.0
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(target_latitude)
        lon2 = math.radians(target_longitude)
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c

    def _build_environment(self, latitude: float, longitude: float) -> Dict[str, Any]:
        try:
            return self.weather_service.get_environment_context(latitude, longitude)
        except WeatherServiceError as exc:
            logger.warning("Weather lookup failed for (%s, %s): %s", latitude, longitude, exc)
            return {
                "air_quality_index": None,
                "pm2_5": None,
                "pm10": None,
                "temperature_c": None,
                "humidity_percent": None,
            }

    def _build_commute(self, latitude: float, longitude: float) -> Dict[str, Any]:
        try:
            return self.mapbox_service.get_travel_times(latitude, longitude)
        except MapboxServiceError as exc:
            logger.warning("Mapbox lookup failed for (%s, %s): %s", latitude, longitude, exc)
            return {
                "commute_time_to_city_center_min": None,
                "travel_time_to_airport": None,
                "travel_time_to_nearest_metro": None,
            }

    def _build_scores(
        self,
        amenities: Dict[str, Any],
        soil: Dict[str, Any],
        market: Dict[str, Any],
        environment: Dict[str, Any],
        commute: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            connectivity = self._connectivity_factors_from_amenities(amenities)
            livability = self._livability_factors_from_amenities_and_soil(amenities, soil)
            investment = self._investment_factors_from_market(market)
            construction = self._construction_factors_from_soil(soil)

            scores = self.scoring_service.calculate_scores(
                connectivity,
                livability,
                investment,
                construction,
            )
            scores["property_grade"] = self._derive_property_grade(scores)
            if environment.get("air_quality_index") is not None:
                scores["air_quality_index"] = int(environment.get("air_quality_index"))
            if commute.get("commute_time_to_city_center_min") is not None:
                scores["commute_time_to_city_center_min"] = int(commute.get("commute_time_to_city_center_min"))
            if soil.get("flood_risk_zone"):
                scores["flood_risk_zone"] = soil.get("flood_risk_zone")
            if soil.get("construction_suitability"):
                scores["construction_suitability"] = soil.get("construction_suitability")
            return scores
        except ScoringServiceError as exc:
            logger.warning("Score generation failed: %s", exc)
            return {"error": "Unable to generate property scores."}

    def _connectivity_factors_from_amenities(self, amenities: Dict[str, Any]) -> ConnectivityFactors:
        return ConnectivityFactors(
            schools_count=self._safe_count(amenities.get("schools")),
            hospitals_count=self._safe_count(amenities.get("hospitals")),
            bus_stops_count=self._safe_count(amenities.get("bus_stops")),
            metro_count=self._safe_count(amenities.get("metro")),
            parks_count=self._safe_count(amenities.get("parks")),
        )

    def _livability_factors_from_amenities_and_soil(
        self,
        amenities: Dict[str, Any],
        soil: Dict[str, Any],
    ) -> LivabilityFactors:
        return LivabilityFactors(
            schools_count=self._safe_count(amenities.get("schools")),
            hospitals_count=self._safe_count(amenities.get("hospitals")),
            parks_count=self._safe_count(amenities.get("parks")),
            water_table_depth=float(soil.get("water_table_depth_m", 0.0) or 0.0),
        )

    def _investment_factors_from_market(self, market: Dict[str, Any]) -> InvestmentFactors:
        return InvestmentFactors(
            price_per_sqft=float(market.get("price_per_sqft", 0.0) or 0.0),
            historical_growth_percent=float(market.get("historical_growth_percent", 0.0) or 0.0),
            future_growth_percent=float(market.get("future_growth_percent", 0.0) or 0.0),
            rental_yield_percent=float(market.get("rental_yield_percent", 0.0) or 0.0),
            roi_index=float(market.get("roi_index", 0.0) or 0.0),
        )

    def _construction_factors_from_soil(self, soil: Dict[str, Any]) -> ConstructionFactors:
        return ConstructionFactors(
            bearing_capacity_kpa=float(soil.get("bearing_capacity_kpa", 0.0) or 0.0),
            water_table_depth_m=float(soil.get("water_table_depth_m", 0.0) or 0.0),
            construction_suitability=str(soil.get("construction_suitability", "poor")) or "poor",
        )

    @staticmethod
    def _safe_count(source: Optional[Dict[str, Any]]) -> int:
        if not source:
            return 0
        count = source.get("count")
        if isinstance(count, int) and count >= 0:
            return count
        try:
            return int(count or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _derive_property_grade(scores: Dict[str, Any]) -> str:
        overall_score = scores.get("overall_score", 0)
        if overall_score >= 80:
            return "A"
        if overall_score >= 70:
            return "B"
        if overall_score >= 60:
            return "C"
        if overall_score >= 50:
            return "D"
        return "E"

    def _build_location_summary(self, location: Dict[str, Any], soil: Dict[str, Any], market: Dict[str, Any], buyer: Dict[str, Any]) -> str:
        locality_name = location.get("matched_locality") or location.get("city") or "the selected locality"
        price = market.get("current_price_sqft") or market.get("price_per_sqft") or 0
        suitability = soil.get("construction_suitability") or "unknown"
        return (
            f"{locality_name} combines {suitability.lower()} construction viability with market pricing of ₹{price:,.0f}/sqft "
            f"and {buyer.get('schools_nearby', 0)} nearby schools."
        )

    def _build_strengths(self, soil: Dict[str, Any], market: Dict[str, Any], buyer: Dict[str, Any]) -> List[str]:
        strengths = []
        if soil.get("construction_suitability") in {"Good", "Excellent"}:
            strengths.append("Strong construction feasibility")
        if (market.get("roi_percentage") or market.get("roi_index") or 0) >= 70:
            strengths.append("High investment upside")
        if buyer.get("schools_nearby", 0) > 0:
            strengths.append("Established education ecosystem")
        return strengths or ["Balanced residential investment profile"]

    def _build_weaknesses(self, soil: Dict[str, Any], market: Dict[str, Any], buyer: Dict[str, Any]) -> List[str]:
        weaknesses = []
        if (soil.get("flood_risk_zone") or "").lower() == "high":
            weaknesses.append("Elevated flood exposure")
        if buyer.get("air_quality_index") is not None and buyer.get("air_quality_index", 0) >= 150:
            weaknesses.append("Air quality concerns")
        if (market.get("risk_score") or 0) >= 60:
            weaknesses.append("Higher market volatility")
        return weaknesses or ["Limited live-API context available"]

    def _build_investment_recommendation(self, scores: Dict[str, Any], market: Dict[str, Any]) -> str:
        overall_score = scores.get("overall_score", 0)
        if overall_score >= 75:
            return "Prioritize this parcel for long-term capital appreciation and premium residential development."
        if overall_score >= 60:
            return "This is a viable medium-term investment with balanced construction and market potential."
        return "Proceed with caution and validate the parcel against additional due diligence before acquisition."

    def _build_construction_recommendation(self, soil: Dict[str, Any], scores: Dict[str, Any]) -> str:
        suitability = (soil.get("construction_suitability") or "Unknown").lower()
        if suitability in {"excellent", "good"} and scores.get("construction_score", 0) >= 60:
            return "Proceed with standard high-rise or mid-rise development using conventional foundations and drainage controls."
        return "Use conservative foundation design, groundwater controls, and site-specific geotechnical validation."

    @staticmethod
    def _nearest_distance_km(source: Optional[Dict[str, Any]]) -> Optional[float]:
        if not source:
            return None
        nearest_distance_m = source.get("nearest_distance_m")
        if nearest_distance_m in (None, ""):
            return None
        try:
            return round(float(nearest_distance_m) / 1000.0, 2)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _top_names(source: Optional[Dict[str, Any]]) -> List[str]:
        if not source:
            return []
        names = source.get("names") or []
        if not isinstance(names, list):
            return []
        return [str(name) for name in names[:5]]
