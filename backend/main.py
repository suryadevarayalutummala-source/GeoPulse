from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.ai_context_builder import AIContextBuilder
from services.geocoder_service import GeocoderService
from utils.polygon_utils import (
    calculate_centroid,
    polygon_to_geojson,
)

app = FastAPI(
    title="Smart Infrastructure & Property Intelligence Platform",
    version="1.0.0",
)


class PolygonRequest(BaseModel):
    polygon: List[List[float]] = Field(
        ...,
        min_length=3,
        description="Polygon coordinates in [longitude, latitude] format",
    )


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "message": "Smart Infrastructure Backend Running"
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok"
    }


@app.post("/api/v1/ai-context/polygon")
def polygon_context(payload: PolygonRequest) -> Dict[str, Any]:
    try:
        longitude, latitude = calculate_centroid(payload.polygon)

        geocoder = GeocoderService()
        detected_locality = geocoder.detect_locality(latitude=latitude, longitude=longitude)
        location = {
            "latitude": latitude,
            "longitude": longitude,
            "matched_locality": detected_locality,
            "display_name": detected_locality or "Unknown",
        }

        builder = AIContextBuilder()
        context = builder.build_context(
            latitude=latitude,
            longitude=longitude,
        )

        return {
            "centroid": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "detected_locality": detected_locality,
            "location": location,
            "geojson": polygon_to_geojson(payload.polygon),
            "context": context,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc