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

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "soil_data.json"
PLOTS_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "plots_final.json"


class SoilServiceError(Exception):
    """Base exception for soil service failures."""


class SoilDataNotFoundError(SoilServiceError):
    """Raised when the soil data file cannot be found."""


class SoilDataInvalidError(SoilServiceError):
    """Raised when the soil data file content is invalid."""


class SoilDatasetEmptyError(SoilServiceError):
    """Raised when the soil data file contains no entries."""


@dataclass(frozen=True)
class SoilRegionRecord:
    region: str
    latitude: float
    longitude: float
    soil_type: str
    bearing_capacity_kpa: float
    water_table_depth_m: float
    flood_risk_zone: str
    max_permissible_floors: int
    utility_access: str
    construction_cost_estimate_per_sqft: float
    construction_suitability: str
    foundation_recommendation: str
    groundwater_risk: str
    excavation_difficulty: str
    pH: float
    organic_matter_percent: float
    drainage: str
    texture: str
    depth_cm: int
    suitability_for_agriculture: str
    recommended_crops: List[str]
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "region": self.region,
            "name": self.region,
            "soil_type": self.soil_type,
            "bearing_capacity_kpa": self.bearing_capacity_kpa,
            "water_table_depth_m": self.water_table_depth_m,
            "flood_risk_zone": self.flood_risk_zone,
            "max_permissible_floors": self.max_permissible_floors,
            "utility_access": self.utility_access,
            "construction_cost_estimate_per_sqft": self.construction_cost_estimate_per_sqft,
            "construction_suitability": self.construction_suitability,
            "foundation_recommendation": self.foundation_recommendation,
            "groundwater_risk": self.groundwater_risk,
            "excavation_difficulty": self.excavation_difficulty,
            "pH": self.pH,
            "organic_matter_percent": self.organic_matter_percent,
            "drainage": self.drainage,
            "texture": self.texture,
            "depth_cm": self.depth_cm,
            "suitability_for_agriculture": self.suitability_for_agriculture,
            "recommended_crops": self.recommended_crops,
            "notes": self.notes,
            "construction_suitability": self.construction_suitability,
        }


class SoilService:
    """Service to load curated soil engineering data and return the nearest locality profile."""

    def __init__(self, data_path: Path = DATA_FILE) -> None:
        self.data_path = data_path
        self._cache: Optional[List[SoilRegionRecord]] = None

    def load_data(self) -> List[SoilRegionRecord]:
        """Load soil dataset from JSON and cache it after the first read."""
        if self._cache is not None:
            return self._cache

        try:
            raw_text = self._read_data_file()
            raw_entries = self._parse_json(raw_text)
            records = self._parse_records(raw_entries)
        except SoilServiceError:
            raise
        except Exception as exc:
            logger.error("Unexpected error loading soil data: %s", exc)
            raise SoilDataInvalidError("Unable to load soil data") from exc

        if not records:
            logger.error("Soil dataset is empty: %s", self.data_path)
            raise SoilDatasetEmptyError("soil dataset contains no entries")

        self._cache = records
        logger.info("Loaded %d soil dataset entries from %s", len(records), self.data_path)
        return records

    def _read_data_file(self) -> str:
        if not self.data_path.exists():
            logger.error("Soil data file not found: %s", self.data_path)
            raise SoilDataNotFoundError(f"Soil data file not found: {self.data_path}")

        try:
            return self.data_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Unable to read soil data file: %s", exc)
            raise SoilServiceError("Unable to read soil data file") from exc

    def _parse_json(self, raw_text: str) -> List[Dict[str, object]]:
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.error("Soil data JSON is invalid: %s", exc)
            raise SoilDataInvalidError("Soil data JSON is invalid") from exc

        if not isinstance(payload, list):
            logger.error("Soil data JSON root element is not a list")
            raise SoilDataInvalidError("Soil data must be a JSON array")

        return payload

    def _parse_records(self, raw_entries: List[Dict[str, object]]) -> List[SoilRegionRecord]:
        records: List[SoilRegionRecord] = []
        for index, entry in enumerate(raw_entries):
            if not isinstance(entry, dict):
                logger.error("Soil data entry at index %s is invalid: %s", index, entry)
                raise SoilDataInvalidError("Each soil data entry must be an object")
            records.append(self._parse_entry(entry, index))
        return records

    def _parse_entry(self, entry: Dict[str, object], index: int) -> SoilRegionRecord:
        try:
            bearing_capacity = float(entry.get("bearing_capacity_kpa", 0.0))
            water_table = float(entry.get("water_table_depth_m", 0.0))
            flood_zone = str(entry.get("flood_risk_zone", "Medium")).strip()
            max_floors = int(entry.get("max_permissible_floors", 6))
            utility_access = str(entry.get("utility_access", "Moderate")).strip()
            cost_estimate = float(entry.get("construction_cost_estimate_per_sqft", 0.0))
            construction_suitability = str(entry.get("construction_suitability", self._derive_suitability(bearing_capacity, water_table, flood_zone))).strip()
            foundation_recommendation = self._derive_foundation(bearing_capacity, water_table, flood_zone)
            groundwater_risk = self._derive_groundwater_risk(water_table)
            excavation_difficulty = self._derive_excavation_difficulty(soil_type=str(entry.get("soil_type", "")), water_table=water_table)
            return SoilRegionRecord(
                region=str(entry.get("region") or entry.get("name") or "").strip(),
                latitude=float(entry["latitude"]),
                longitude=float(entry["longitude"]),
                soil_type=str(entry.get("soil_type", "Unknown")).strip(),
                bearing_capacity_kpa=bearing_capacity,
                water_table_depth_m=water_table,
                flood_risk_zone=flood_zone,
                max_permissible_floors=max_floors,
                utility_access=utility_access,
                construction_cost_estimate_per_sqft=cost_estimate,
                construction_suitability=construction_suitability,
                foundation_recommendation=foundation_recommendation,
                groundwater_risk=groundwater_risk,
                excavation_difficulty=excavation_difficulty,
                pH=float(entry.get("pH", 7.0)),
                organic_matter_percent=float(entry.get("organic_matter_percent", 1.0)),
                drainage=str(entry.get("drainage", "Unknown")).strip(),
                texture=str(entry.get("texture", "Unknown")).strip(),
                depth_cm=int(entry.get("depth_cm", 0)),
                suitability_for_agriculture=str(entry.get("suitability_for_agriculture", "Unknown")).strip(),
                recommended_crops=list(entry.get("recommended_crops", [])),
                notes=str(entry.get("notes", "")).strip(),
            )
        except KeyError as exc:
            logger.error("Missing required soil data field at index %s: %s", index, exc)
            raise SoilDataInvalidError("Missing required soil data field") from exc
        except (TypeError, ValueError) as exc:
            logger.error("Invalid soil data value at index %s: %s", index, exc)
            raise SoilDataInvalidError("Invalid soil data value") from exc

    @staticmethod
    def _derive_suitability(bearing_capacity: float, water_table: float, flood_zone: str) -> str:
        if bearing_capacity >= 180 and water_table <= 4.0 and flood_zone.lower() == "low":
            return "Excellent"
        if bearing_capacity >= 150 and water_table <= 5.0 and flood_zone.lower() != "high":
            return "Good"
        if bearing_capacity >= 130:
            return "Moderate"
        return "Fair"

    @staticmethod
    def _derive_foundation(bearing_capacity: float, water_table: float, flood_zone: str) -> str:
        if bearing_capacity >= 180 and water_table <= 4.0:
            return "Raft foundation with controlled groundwater management"
        if flood_zone.lower() == "high":
            return "Pile foundation with elevated plinth and water-resistant detailing"
        if water_table >= 5.0:
            return "Strip footing with dewatering and moisture barriers"
        return "Isolated footing with standard substructure detailing"

    @staticmethod
    def _derive_groundwater_risk(water_table: float) -> str:
        if water_table >= 5.0:
            return "High"
        if water_table >= 3.5:
            return "Moderate"
        return "Low"

    @staticmethod
    def _derive_excavation_difficulty(soil_type: str, water_table: float) -> str:
        if "clay" in soil_type.lower() and water_table >= 4.0:
            return "High"
        if "sandy" in soil_type.lower() or water_table >= 3.5:
            return "Moderate"
        return "Low"

    def _haversine_distance(self, latitude: float, longitude: float, record: SoilRegionRecord) -> float:
        """Calculate Haversine distance in meters between a point and a soil region."""
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(record.latitude)
        lon2 = math.radians(record.longitude)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371000.0 * c

    @staticmethod
    def _haversine_between_points(latitude: float, longitude: float, target_latitude: float, target_longitude: float) -> float:
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(target_latitude)
        lon2 = math.radians(target_longitude)

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
            distance = self._haversine_between_points(latitude, longitude, float(plot_latitude), float(plot_longitude))
            if distance < best_distance:
                best_distance = distance
                best_plot = plot
        return best_plot

    def find_nearest_region(self, latitude: float, longitude: float, plot_id: Optional[str] = None) -> Tuple[SoilRegionRecord, float]:
        """Find the soil dataset entry for the matching plot cluster, falling back to the nearest dataset entry."""
        records = self.load_data()

        plot_record = self._resolve_plot_record(latitude, longitude, plot_id)
        cluster_name = str(plot_record.get("cluster", "")).strip() if plot_record else ""
        if cluster_name:
            for record in records:
                if record.region.lower() == cluster_name.lower():
                    logger.info(
                        "Selected soil region for plot %s via cluster %s",
                        plot_record.get("plot_id"),
                        cluster_name,
                    )
                    return record, self._haversine_distance(latitude, longitude, record)

        nearest = min(
            records,
            key=lambda record: self._haversine_distance(latitude, longitude, record),
        )
        distance = self._haversine_distance(latitude, longitude, nearest)
        logger.info(
            "Nearest soil region for (%s, %s) is %s at %.2f meters.",
            latitude,
            longitude,
            nearest.region,
            distance,
        )
        return nearest, distance

    def get_soil_information(self, latitude: float, longitude: float, plot_id: Optional[str] = None) -> Dict[str, object]:
        """Return soil information for the plot-matched dataset region, falling back to the nearest dataset region."""
        nearest, distance = self.find_nearest_region(latitude, longitude, plot_id)
        info = nearest.to_dict()
        info["region"] = nearest.region
        info["distance_to_dataset_m"] = distance
        logger.info(
            "Soil information retrieved for (%s, %s): %s", latitude, longitude, info
        )
        return info
