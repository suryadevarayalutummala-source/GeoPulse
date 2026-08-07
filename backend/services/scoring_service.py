from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _validate_non_negative(value: float, name: str) -> float:
    if value < 0:
        logger.error("Invalid value for %s: %s", name, value)
        raise InvalidScoreInputError(f"{name} must be non-negative")
    return value


def _normalize_percentage(value: float, name: str) -> float:
    _validate_non_negative(value, name)
    if value > 100:
        logger.warning("Clamping percentage %s to 100: %s", name, value)
    return _clamp(value)


class ScoringServiceError(Exception):
    """Base exception for scoring service failures."""


class InvalidScoreInputError(ScoringServiceError):
    """Raised when a score input is invalid."""


@dataclass(frozen=True)
class ConnectivityFactors:
    schools_count: int
    hospitals_count: int
    bus_stops_count: int
    metro_count: int
    parks_count: int


@dataclass(frozen=True)
class LivabilityFactors:
    schools_count: int
    hospitals_count: int
    parks_count: int
    water_table_depth: float


@dataclass(frozen=True)
class InvestmentFactors:
    price_per_sqft: float
    historical_growth_percent: float
    future_growth_percent: float
    rental_yield_percent: float
    roi_index: float


@dataclass(frozen=True)
class ConstructionFactors:
    bearing_capacity_kpa: float
    water_table_depth_m: float
    construction_suitability: str


class ScoringService:
    """Service for calculating infrastructure and investment scores."""

    def _normalize_count(self, count: int, name: str) -> int:
        if count < 0:
            raise InvalidScoreInputError(f"{name} must be non-negative")
        return count

    def _normalize_depth(self, value: float, name: str) -> float:
        _validate_non_negative(value, name)
        return value

    def calculate_connectivity_score(self, factors: ConnectivityFactors) -> int:
        """Calculate a connectivity score between 0 and 100."""
        schools_count = self._normalize_count(factors.schools_count, "schools_count")
        hospitals_count = self._normalize_count(factors.hospitals_count, "hospitals_count")
        bus_stops_count = self._normalize_count(factors.bus_stops_count, "bus_stops_count")
        metro_count = self._normalize_count(factors.metro_count, "metro_count")
        parks_count = self._normalize_count(factors.parks_count, "parks_count")

        score = (
            min(25.0, 8.0 * math.log1p(schools_count))
            + min(25.0, 10.0 * math.log1p(hospitals_count))
            + min(20.0, 5.0 * math.log1p(bus_stops_count))
            + min(20.0, 12.0 * math.log1p(metro_count))
            + min(20.0, 7.0 * math.log1p(parks_count))
        )

        result = int(round(_clamp(score)))
        logger.info(
            "Calculated connectivity score=%s from %s",
            result,
            factors,
        )
        return result

    def calculate_livability_score(self, factors: LivabilityFactors) -> int:
        """Calculate a livability score between 0 and 100."""
        schools = self._normalize_count(factors.schools_count, "schools_count")
        hospitals = self._normalize_count(factors.hospitals_count, "hospitals_count")
        parks = self._normalize_count(factors.parks_count, "parks_count")
        water_table_depth = self._normalize_depth(factors.water_table_depth, "water_table_depth")

        schools_score = min(20.0, 8.0 * math.log1p(schools))
        hospitals_score = min(20.0, 10.0 * math.log1p(hospitals))
        parks_score = min(35.0, 10.0 * math.log1p(parks))
        water_score = min(25.0, (water_table_depth / 5.0) * 25.0)

        score = schools_score + hospitals_score + parks_score + water_score
        result = int(round(_clamp(score)))
        logger.info(
            "Calculated livability score=%s from %s",
            result,
            factors,
        )
        return result

    def calculate_investment_score(self, factors: InvestmentFactors) -> int:
        """Calculate an investment score between 0 and 100."""
        _validate_non_negative(factors.price_per_sqft, "price_per_sqft")
        historical_growth_percent = _normalize_percentage(
            factors.historical_growth_percent, "historical_growth_percent"
        )
        future_growth_percent = _normalize_percentage(
            factors.future_growth_percent, "future_growth_percent"
        )
        rental_yield_percent = _normalize_percentage(
            factors.rental_yield_percent, "rental_yield_percent"
        )
        roi_index = _normalize_percentage(factors.roi_index, "roi_index")

        price_factor = min(15.0, 15.0 * (200.0 / max(factors.price_per_sqft, 1.0)))
        growth_score = min(35.0, 1.5 * (historical_growth_percent + future_growth_percent))
        rental_score = min(30.0, 3.0 * rental_yield_percent)
        roi_score = min(40.0, 1.5 * roi_index)

        score = price_factor + growth_score + rental_score + roi_score
        result = int(round(_clamp(score)))
        logger.info(
            "Calculated investment score=%s from %s",
            result,
            factors,
        )
        return result

    def calculate_construction_score(self, factors: ConstructionFactors) -> int:
        """Calculate a construction score between 0 and 100."""
        _validate_non_negative(factors.bearing_capacity_kpa, "bearing_capacity_kpa")
        water_table_depth_m = self._normalize_depth(
            factors.water_table_depth_m, "water_table_depth_m"
        )

        suitability_map = {
            "excellent": 20.0,
            "good": 16.0,
            "moderate": 12.0,
            "fair": 8.0,
            "poor": 4.0,
        }
        suitability_score = suitability_map.get(
            factors.construction_suitability.strip().lower(), 10.0
        )

        bearing_score = min(50.0, max(0.0, (factors.bearing_capacity_kpa - 75.0) / 3.5))
        water_score = min(30.0, (water_table_depth_m / 10.0) * 30.0)
        score = bearing_score + water_score + suitability_score

        result = int(round(_clamp(score)))
        logger.info(
            "Calculated construction score=%s from %s",
            result,
            factors,
        )
        return result

    def calculate_overall_score(
        self,
        connectivity_score: int,
        livability_score: int,
        investment_score: int,
        construction_score: int,
    ) -> int:
        """Combine component scores into a weighted overall score."""
        for value, name in [
            (connectivity_score, "connectivity_score"),
            (livability_score, "livability_score"),
            (investment_score, "investment_score"),
            (construction_score, "construction_score"),
        ]:
            if not isinstance(value, int) or value < 0 or value > 100:
                logger.error("Invalid component score %s=%s", name, value)
                raise InvalidScoreInputError(
                    f"{name} must be an integer between 0 and 100"
                )

        score = (
            connectivity_score * 0.20
            + livability_score * 0.30
            + investment_score * 0.30
            + construction_score * 0.20
        )
        result = int(round(_clamp(score)))
        logger.info(
            "Calculated overall score=%s from connectivity=%s, livability=%s, investment=%s, construction=%s",
            result,
            connectivity_score,
            livability_score,
            investment_score,
            construction_score,
        )
        return result

    def generate_property_scores(
        self,
        connectivity: ConnectivityFactors,
        livability: LivabilityFactors,
        investment: InvestmentFactors,
        construction: ConstructionFactors,
    ) -> Dict[str, int]:
        """Return component scores and the weighted overall score."""
        connectivity_score = self.calculate_connectivity_score(connectivity)
        livability_score = self.calculate_livability_score(livability)
        investment_score = self.calculate_investment_score(investment)
        construction_score = self.calculate_construction_score(construction)
        overall_score = self.calculate_overall_score(
            connectivity_score,
            livability_score,
            investment_score,
            construction_score,
        )

        result = {
            "connectivity_score": connectivity_score,
            "livability_score": livability_score,
            "investment_score": investment_score,
            "construction_score": construction_score,
            "overall_score": overall_score,
        }
        logger.info("Calculated all property scores: %s", result)
        return result

    calculate_scores = generate_property_scores
