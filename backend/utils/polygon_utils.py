from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, mapping
from shapely.ops import transform

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
PolygonCoordinates = Sequence[Coordinate]
Feature = Dict[str, Any]


class InvalidPolygonError(Exception):
    """Raised when polygon validation or construction fails."""


def _extract_polygon_coordinates(feature: Feature) -> PolygonCoordinates:
    """Extract polygon coordinates from a GeoJSON Feature payload."""
    try:
        geometry = feature["geometry"]
        coordinates = geometry["coordinates"]
        if not coordinates or not isinstance(coordinates, list):
            raise KeyError
        exterior_ring = coordinates[0]
    except (KeyError, TypeError, IndexError) as exc:
        logger.error("Failed to extract polygon coordinates from feature: %s", exc)
        raise InvalidPolygonError("Invalid GeoJSON Feature payload")

    return tuple((float(lon), float(lat)) for lon, lat in exterior_ring)


def _validate_polygon_coordinates(polygon_coordinates: PolygonCoordinates) -> None:
    """Validate polygon coordinates before geometry operations."""
    if not polygon_coordinates:
        logger.error("Polygon coordinates are empty.")
        raise InvalidPolygonError("polygon_coordinates must contain at least four coordinate pairs")

    if len(polygon_coordinates) < 4:
        logger.error(
            "Polygon coordinates contain fewer than 4 points: %s",
            polygon_coordinates,
        )
        raise InvalidPolygonError("polygon_coordinates must contain at least four coordinate pairs")

    for index, point in enumerate(polygon_coordinates):
        if (
            not isinstance(point, (list, tuple))
            or len(point) != 2
            or not all(isinstance(value, (int, float)) for value in point)
        ):
            logger.error("Invalid coordinate at index %s: %s", index, point)
            raise InvalidPolygonError(
                "Each polygon coordinate must be a pair of numeric values [longitude, latitude]"
            )


def _create_polygon(polygon_coordinates: PolygonCoordinates) -> Polygon:
    """Create a valid Shapely Polygon from longitude/latitude pairs."""
    _validate_polygon_coordinates(polygon_coordinates)
    polygon = Polygon(polygon_coordinates)

    if not polygon.is_valid or polygon.is_empty or polygon.area == 0:
        logger.error("Invalid polygon geometry from coordinates: %s", polygon_coordinates)
        raise InvalidPolygonError("polygon_coordinates did not form a valid polygon")

    return polygon


def _build_transformer(polygon: Polygon) -> Transformer:
    """Build a local equal-area transformer based on polygon centroid."""
    centroid = polygon.centroid
    target_crs = CRS.from_proj4(
        f"+proj=aeqd +lat_0={centroid.y} +lon_0={centroid.x} +datum=WGS84 +units=m +no_defs"
    )
    return Transformer.from_crs(CRS.from_epsg(4326), target_crs, always_xy=True)


def calculate_area(polygon_coordinates: PolygonCoordinates) -> float:
    """Calculate the polygon area in square meters.

    Args:
        polygon_coordinates: Sequence of [longitude, latitude] pairs.

    Returns:
        The polygon area in square meters.
    """
    polygon = _create_polygon(polygon_coordinates)
    transformer = _build_transformer(polygon)
    projected_polygon = transform(transformer.transform, polygon)
    area = projected_polygon.area
    logger.info("Calculated polygon area: %.2f m^2", area)
    return area


def calculate_perimeter(polygon_coordinates: PolygonCoordinates) -> float:
    """Calculate the polygon perimeter in meters."""
    polygon = _create_polygon(polygon_coordinates)
    transformer = _build_transformer(polygon)
    projected_polygon = transform(transformer.transform, polygon)
    perimeter = projected_polygon.length
    logger.info("Calculated polygon perimeter: %.2f m", perimeter)
    return perimeter


def calculate_centroid(polygon_coordinates: PolygonCoordinates) -> Coordinate:
    """Return the polygon centroid as (longitude, latitude)."""
    polygon = _create_polygon(polygon_coordinates)
    centroid = polygon.centroid
    result: Coordinate = (centroid.x, centroid.y)
    logger.info("Calculated polygon centroid: %s", result)
    return result


def polygon_to_geojson(polygon_coordinates: PolygonCoordinates) -> Dict[str, Any]:
    """Convert polygon coordinates into a valid GeoJSON Polygon object."""
    polygon = _create_polygon(polygon_coordinates)
    geojson = mapping(polygon)
    logger.info("Converted polygon to GeoJSON Polygon.")
    return geojson


def extract_polygon_coordinates(feature: Feature) -> PolygonCoordinates:
    """Extract coordinates from a GeoJSON Feature payload for a Polygon."""
    return _extract_polygon_coordinates(feature)
