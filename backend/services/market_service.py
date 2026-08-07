from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "market_data.json"
PLOTS_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "plots_final.json"


class MarketServiceError(Exception):
    """Base exception for MarketService failures."""


class MarketDataNotFoundError(MarketServiceError):
    """Raised when the market data file cannot be found."""


class MarketDataInvalidError(MarketServiceError):
    """Raised when market data cannot be parsed or is invalid."""


class MarketDatasetEmptyError(MarketServiceError):
    """Raised when market data contains no entries."""


@dataclass(frozen=True)
class MarketRegionRecord:
    region: str
    latitude: float
    longitude: float
    current_price_sqft: float
    historical_growth_rates: List[float]
    rental_yield_percentage: float
    roi_percentage: float
    risk_score: float
    infrastructure_development_pipeline: List[str]

    def to_dict(self) -> Dict[str, object]:
        historical_growth = self.historical_growth_rates or [0.0]
        historical_growth_percent = float(historical_growth[0]) if historical_growth else 0.0
        future_growth_percent = float(historical_growth[-1]) if historical_growth else 0.0
        return {
            "region": self.region,
            "name": self.region,
            "current_price_sqft": self.current_price_sqft,
            "historical_growth_rates": self.historical_growth_rates,
            "rental_yield_percentage": self.rental_yield_percentage,
            "roi_percentage": self.roi_percentage,
            "risk_score": self.risk_score,
            "infrastructure_development_pipeline": self.infrastructure_development_pipeline,
            "price_per_sqft": self.current_price_sqft,
            "historical_growth_percent": historical_growth_percent,
            "future_growth_percent": future_growth_percent,
            "rental_yield_percent": self.rental_yield_percentage,
            "roi_index": self.roi_percentage,
            "market_trend": "Stable" if self.risk_score >= 60 else "Bullish",
            "infrastructure_projects": self.infrastructure_development_pipeline,
        }


class MarketService:
    """Service that loads curated market data and returns the nearest locality profile."""

    def __init__(self, data_path: Path = DATA_FILE) -> None:
        self.data_path = data_path
        self._cache: Optional[List[MarketRegionRecord]] = None

    def load_data(self) -> List[MarketRegionRecord]:
        """Load market data from JSON and cache it after the first read."""
        if self._cache is not None:
            return self._cache

        raw_text = self._read_data_file()
        entries = self._parse_json(raw_text)
        records = self._parse_records(entries)

        if not records:
            logger.error("Market dataset is empty: %s", self.data_path)
            raise MarketDatasetEmptyError("market dataset contains no entries")

        self._cache = records
        logger.info("Loaded %d market dataset entries from %s", len(records), self.data_path)
        return records

    def _read_data_file(self) -> str:
        if not self.data_path.exists():
            logger.error("Market data file not found: %s", self.data_path)
            raise MarketDataNotFoundError(f"Market data file not found: {self.data_path}")

        try:
            return self.data_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Failed to read market data file: %s", exc)
            raise MarketServiceError("Unable to read market data file") from exc

    def _parse_json(self, raw_text: str) -> List[Dict[str, object]]:
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.error("Market data JSON is invalid: %s", exc)
            raise MarketDataInvalidError("Market data JSON is invalid") from exc

        if not isinstance(payload, list):
            logger.error("Market data JSON root element is not a list")
            raise MarketDataInvalidError("Market data must be a JSON array")

        return payload

    def _parse_records(self, entries: List[Dict[str, object]]) -> List[MarketRegionRecord]:
        records: List[MarketRegionRecord] = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                logger.error("Market data entry at index %s is invalid: %s", index, entry)
                raise MarketDataInvalidError("Each market data entry must be an object")
            records.append(self._parse_entry(entry, index))
        return records

    def _parse_entry(self, entry: Dict[str, object], index: int) -> MarketRegionRecord:
        try:
            historical_growth_rates = entry.get("historical_growth_rates")
            if historical_growth_rates is None:
                historical_growth_rates = [entry.get("historical_growth_percent", 0.0)]
            if not isinstance(historical_growth_rates, list):
                historical_growth_rates = [historical_growth_rates]
            parsed_rates = [float(value) for value in historical_growth_rates]
            return MarketRegionRecord(
                region=str(entry.get("region") or entry.get("name") or "").strip(),
                latitude=float(entry["latitude"]),
                longitude=float(entry["longitude"]),
                current_price_sqft=float(entry.get("current_price_sqft", entry.get("price_per_sqft", 0.0))),
                historical_growth_rates=parsed_rates,
                rental_yield_percentage=float(entry.get("rental_yield_percentage", entry.get("rental_yield_percent", 0.0))),
                roi_percentage=float(entry.get("roi_percentage", entry.get("roi_index", 0.0))),
                risk_score=float(entry.get("risk_score", 0.0)),
                infrastructure_development_pipeline=list(entry.get("infrastructure_development_pipeline", entry.get("infrastructure_projects", []))),
            )
        except KeyError as exc:
            logger.error("Missing required market data field at index %s: %s", index, exc)
            raise MarketDataInvalidError("Missing required market data field") from exc
        except (TypeError, ValueError) as exc:
            logger.error("Invalid market data value at index %s: %s", index, exc)
            raise MarketDataInvalidError("Invalid market data value") from exc

    def _haversine_distance(self, latitude: float, longitude: float, record: MarketRegionRecord) -> float:
        """Calculate Haversine distance in meters between a point and a market region."""
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(record.latitude)
        lon2 = math.radians(record.longitude)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371000.0 * c

    def _load_plot_catalog(self) -> List[Dict[str, object]]:
        if not PLOTS_DATA_FILE.exists():
            return []
        try:
            payload = json.loads(PLOTS_DATA_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        return [plot for plot in payload if isinstance(plot, dict)]

    def _resolve_plot_record(self, latitude: float, longitude: float, plot_id: Optional[str] = None) -> Optional[Dict[str, object]]:
        plot_catalog = self._load_plot_catalog()
        if plot_id:
            for plot in plot_catalog:
                if str(plot.get("plot_id", "")).strip() == str(plot_id).strip():
                    return plot

        best_plot: Optional[Dict[str, object]] = None
        best_distance = float("inf")
        for plot in plot_catalog:
            coords = plot.get("coordinates") or {}
            plot_latitude = coords.get("latitude")
            plot_longitude = coords.get("longitude")
            if plot_latitude is None or plot_longitude is None:
                continue
            distance = self._haversine_distance(latitude, longitude, MarketRegionRecord(
                region=str(plot.get("cluster") or ""),
                latitude=float(plot_latitude),
                longitude=float(plot_longitude),
                current_price_sqft=0.0,
                historical_growth_rates=[],
                rental_yield_percentage=0.0,
                roi_percentage=0.0,
                risk_score=0.0,
                infrastructure_development_pipeline=[],
            ))
            if distance < best_distance:
                best_distance = distance
                best_plot = plot
        return best_plot

    def find_nearest_region(self, latitude: float, longitude: float, plot_id: Optional[str] = None) -> Tuple[MarketRegionRecord, float]:
        """Find the market region for the matching plot cluster, falling back to the nearest dataset region."""
        records = self.load_data()

        plot_record = self._resolve_plot_record(latitude, longitude, plot_id)
        cluster_name = str(plot_record.get("cluster", "")).strip() if plot_record else ""
        if cluster_name:
            for record in records:
                if record.region.lower() == cluster_name.lower():
                    logger.info(
                        "Selected market region for plot %s via cluster %s",
                        plot_record.get("plot_id"),
                        cluster_name,
                    )
                    return record, self._haversine_distance(latitude, longitude, record)

        nearest = min(records, key=lambda record: self._haversine_distance(latitude, longitude, record))
        distance = self._haversine_distance(latitude, longitude, nearest)

        logger.info(
            "Nearest market region for (%s, %s) is %s at %.2f meters.",
            latitude,
            longitude,
            nearest.region,
            distance,
        )
        return nearest, distance

    def get_market_information(self, latitude: float, longitude: float, plot_id: Optional[str] = None) -> Dict[str, object]:
        """Return market information for the plot-matched dataset region, falling back to the nearest dataset region."""
        nearest, distance = self.find_nearest_region(latitude, longitude, plot_id)
        info = nearest.to_dict()
        info["distance_to_dataset_m"] = distance
        logger.info(
            "Market information retrieved for (%s, %s): %s", latitude, longitude, info
        )
        return info
