"""Shared lat/lon validation for Hyderabad demo area."""

from __future__ import annotations

from fastapi import HTTPException

from config.geo_reference_points import HYDERABAD_BBOX


def validate_hyderabad_coords(*, longitude: float, latitude: float) -> None:
    box = HYDERABAD_BBOX
    if not (box["min_lat"] <= latitude <= box["max_lat"]):
        raise HTTPException(
            status_code=400,
            detail="Latitude out of Hyderabad demo bounds",
        )
    if not (box["min_lon"] <= longitude <= box["max_lon"]):
        raise HTTPException(
            status_code=400,
            detail="Longitude out of Hyderabad demo bounds",
        )
