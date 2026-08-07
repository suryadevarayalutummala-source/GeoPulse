from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class LocationSchema(BaseModel):
    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="Latitude in decimal degrees", example=12.9716
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Longitude in decimal degrees", example=77.5946
    )
    city: Optional[str] = Field(None, max_length=100, example="Bengaluru")
    district: Optional[str] = Field(None, max_length=100, example="Bengaluru Urban")
    state: Optional[str] = Field(None, max_length=100, example="Karnataka")
    country: Optional[str] = Field(None, max_length=100, example="India")
    display_name: Optional[str] = Field(None, max_length=250, example="MG Road, Bengaluru, Karnataka, India")
    postcode: Optional[str] = Field(None, max_length=20, example="560001")

    model_config = {
        "extra": "forbid",
        "anystr_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "latitude": 12.9716,
                "longitude": 77.5946,
                "city": "Bengaluru",
                "district": "Bengaluru Urban",
                "state": "Karnataka",
                "country": "India",
                "display_name": "MG Road, Bengaluru, Karnataka, India",
                "postcode": "560001",
            }
        },
    }


class AmenityResultSchema(BaseModel):
    count: int = Field(..., ge=0, description="Number of nearby amenities", example=5)
    names: List[str] = Field(..., description="Amenity names near the location", example=["School A", "School B"])
    class CoordinateSchema(BaseModel):
        latitude: float = Field(..., description="Latitude in decimal degrees")
        longitude: float = Field(..., description="Longitude in decimal degrees")

    coordinates: List[CoordinateSchema] = Field(
        ..., description="Amenity coordinates as a list of latitude/longitude pairs"
    )

    nearest_distance_m: Optional[float] = Field(None, ge=0.0, description="Distance to the nearest amenity in meters", example=120.5)

    # Pydantic will validate `CoordinateSchema` entries automatically; no custom validator required.

    model_config = {
        "extra": "forbid",
        "anystr_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "count": 3,
                "names": ["School A", "School B", "School C"],
                "coordinates": [
                    {"latitude": 12.9718, "longitude": 77.5942},
                    {"latitude": 12.9720, "longitude": 77.5950},
                ],
                "nearest_distance_m": 75.4,
            }
        },
    }


class AmenitiesSchema(BaseModel):
    schools: AmenityResultSchema
    hospitals: AmenityResultSchema
    parks: AmenityResultSchema
    bus_stops: AmenityResultSchema
    metro: AmenityResultSchema
    shopping_malls: AmenityResultSchema

    model_config = {
        "extra": "forbid",
        "anystr_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "schools": {
                    "count": 2,
                    "names": ["School A", "School B"],
                    "coordinates": [{"latitude": 12.9718, "longitude": 77.5942}],
                    "nearest_distance_m": 90.0,
                },
                "hospitals": {
                    "count": 1,
                    "names": ["Hospital X"],
                    "coordinates": [{"latitude": 12.9723, "longitude": 77.5935}],
                    "nearest_distance_m": 130.0,
                },
                "parks": {
                    "count": 1,
                    "names": ["Central Park"],
                    "coordinates": [{"latitude": 12.9730, "longitude": 77.5955}],
                    "nearest_distance_m": 200.0,
                },
                "bus_stops": {
                    "count": 4,
                    "names": ["Bus Stop A"],
                    "coordinates": [{"latitude": 12.9711, "longitude": 77.5948}],
                    "nearest_distance_m": 35.0,
                },
                "metro": {
                    "count": 1,
                    "names": ["Metro Station"],
                    "coordinates": [{"latitude": 12.9740, "longitude": 77.5960}],
                    "nearest_distance_m": 420.0,
                },
                "shopping_malls": {
                    "count": 1,
                    "names": ["Mall Z"],
                    "coordinates": [{"latitude": 12.9750, "longitude": 77.5970}],
                    "nearest_distance_m": 560.0,
                },
            }
        },
    }


class SoilSchema(BaseModel):
    region: str = Field(..., min_length=1, max_length=100, example="Central Bengaluru")
    soil_type: str = Field(..., min_length=1, max_length=100, example="Loamy")
    bearing_capacity_kpa: float = Field(..., ge=0.0, example=180.0)
    water_table_depth_m: float = Field(..., ge=0.0, example=2.5)
    construction_suitability: str = Field(..., min_length=1, max_length=100, example="Good")
    pH: Optional[float] = Field(None, ge=0.0, le=14.0, example=7.4)
    organic_matter_percent: Optional[float] = Field(None, ge=0.0, le=100.0, example=1.2)
    drainage: Optional[str] = Field(None, max_length=50, example="Well-drained")
    texture: Optional[str] = Field(None, max_length=50, example="Sandy loam")
    depth_cm: Optional[int] = Field(None, ge=0, example=80)
    suitability_for_agriculture: Optional[str] = Field(None, max_length=50, example="Low")
    recommended_crops: Optional[List[str]] = Field(None, example=["Neem", "Tamarind"])
    notes: Optional[str] = Field(None, max_length=500, example="Urbanized area with artificial fill.")
    distance_to_dataset_m: float = Field(..., ge=0.0, example=1200.0)

    model_config = {
        "extra": "forbid",
        "anystr_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "region": "Central Bengaluru",
                "soil_type": "Loamy",
                "bearing_capacity_kpa": 180.0,
                "water_table_depth_m": 2.5,
                "construction_suitability": "Good",
                "distance_to_dataset_m": 1200.0,
            }
        },
    }


class MarketSchema(BaseModel):
    region: str = Field(..., min_length=1, max_length=100, example="Central Bengaluru")
    price_per_sqft: float = Field(..., ge=0.0, example=8500.0)
    historical_growth_percent: float = Field(..., ge=0.0, le=100.0, example=7.4)
    future_growth_percent: float = Field(..., ge=0.0, le=100.0, example=6.2)
    rental_yield_percent: float = Field(..., ge=0.0, le=100.0, example=4.5)
    roi_index: float = Field(..., ge=0.0, le=100.0, example=72.0)
    market_trend: Optional[str] = Field(None, max_length=50, example="Bullish")
    infrastructure_projects: Optional[List[str]] = Field(None, example=["Metro Phase 2", "Outer Ring Road"])
    distance_to_dataset_m: float = Field(..., ge=0.0, example=950.0)

    model_config = {
        "extra": "forbid",
        "anystr_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "region": "Central Bengaluru",
                "price_per_sqft": 8500.0,
                "historical_growth_percent": 7.4,
                "future_growth_percent": 6.2,
                "rental_yield_percent": 4.5,
                "roi_index": 72.0,
                "distance_to_dataset_m": 950.0,
            }
        },
    }


class ScoresSchema(BaseModel):
    connectivity_score: int = Field(..., ge=0, le=100, example=82)
    livability_score: int = Field(..., ge=0, le=100, example=76)
    investment_score: int = Field(..., ge=0, le=100, example=68)
    construction_score: int = Field(..., ge=0, le=100, example=71)
    overall_score: int = Field(..., ge=0, le=100, example=74)

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "connectivity_score": 82,
                "livability_score": 76,
                "investment_score": 68,
                "construction_score": 71,
                "overall_score": 74,
            }
        },
    }


class AIContextResponseSchema(BaseModel):
    location: LocationSchema
    amenities: AmenitiesSchema
    soil: SoilSchema
    market: MarketSchema
    scores: ScoresSchema

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "city": "Bengaluru",
                    "district": "Bengaluru Urban",
                    "state": "Karnataka",
                    "country": "India",
                    "display_name": "MG Road, Bengaluru, Karnataka, India",
                    "postcode": "560001",
                },
                "amenities": {
                    "schools": {
                        "count": 2,
                        "names": ["School A", "School B"],
                        "coordinates": [{"latitude": 12.9718, "longitude": 77.5942}],
                        "nearest_distance_m": 90.0,
                    },
                    "hospitals": {
                        "count": 1,
                        "names": ["Hospital X"],
                        "coordinates": [{"latitude": 12.9723, "longitude": 77.5935}],
                        "nearest_distance_m": 130.0,
                    },
                    "parks": {
                        "count": 1,
                        "names": ["Central Park"],
                        "coordinates": [{"latitude": 12.9730, "longitude": 77.5955}],
                        "nearest_distance_m": 200.0,
                    },
                    "bus_stops": {
                        "count": 4,
                        "names": ["Bus Stop A"],
                        "coordinates": [{"latitude": 12.9711, "longitude": 77.5948}],
                        "nearest_distance_m": 35.0,
                    },
                    "metro": {
                        "count": 1,
                        "names": ["Metro Station"],
                        "coordinates": [{"latitude": 12.9740, "longitude": 77.5960}],
                        "nearest_distance_m": 420.0,
                    },
                    "shopping_malls": {
                        "count": 1,
                        "names": ["Mall Z"],
                        "coordinates": [{"latitude": 12.9750, "longitude": 77.5970}],
                        "nearest_distance_m": 560.0,
                    },
                },
                "soil": {
                    "region": "Central Bengaluru",
                    "soil_type": "Loamy",
                    "bearing_capacity_kpa": 180.0,
                    "water_table_depth_m": 2.5,
                    "construction_suitability": "Good",
                    "pH": 7.4,
                    "organic_matter_percent": 1.2,
                    "drainage": "Well-drained",
                    "texture": "Sandy loam",
                    "depth_cm": 80,
                    "suitability_for_agriculture": "Low",
                    "recommended_crops": ["Neem", "Tamarind"],
                    "notes": "Urbanized area with artificial fill.",
                    "distance_to_dataset_m": 1200.0,
                },
                "market": {
                    "region": "Central Bengaluru",
                    "price_per_sqft": 8500.0,
                    "historical_growth_percent": 7.4,
                    "future_growth_percent": 6.2,
                    "rental_yield_percent": 4.5,
                    "roi_index": 72.0,
                    "distance_to_dataset_m": 950.0,
                },
                "scores": {
                    "connectivity_score": 82,
                    "livability_score": 76,
                    "investment_score": 68,
                    "construction_score": 71,
                    "overall_score": 74,
                },
            }
        },
    }


class PolygonRequestSchema(BaseModel):
    polygon: List[List[float]] = Field(
        ...,
        min_items=3,
        description="Polygon defined as an ordered list of [longitude, latitude] coordinate pairs",
        example=[[77.5946, 12.9716], [77.5950, 12.9720], [77.5940, 12.9725]],
    )

    @field_validator("polygon", mode="before")
    def validate_polygon(cls, value):
        if not isinstance(value, list):
            raise TypeError("polygon must be a list of coordinate pairs")
        for item in value:
            if not isinstance(item, list) or len(item) != 2:
                raise ValueError("each polygon vertex must be a list of two numeric values")
            longitude, latitude = item
            if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
                raise TypeError("polygon coordinates must be numeric")
        return value

    @model_validator(mode="after")
    def validate_polygon(self):
        if self.polygon is None or len(self.polygon) < 3:
            raise ValueError("polygon must contain at least three vertices")
        return self

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "polygon": [[77.5946, 12.9716], [77.5950, 12.9720], [77.5940, 12.9725]],
            }
        },
    }
