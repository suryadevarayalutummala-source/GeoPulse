"""
Single source of truth for Hyderabad demo geological reference points.

ESTIMATED_DEMO_VALUES — soil numbers below are demo estimates for IDW only.
Coordinate convention: longitude first, then latitude (GeoJSON / Mapbox).
"""

from __future__ import annotations

# ESTIMATED_DEMO_VALUES — replace this entire list when real geotech data arrives.
GEO_REFERENCE_POINTS: list[dict] = [
    {
        "locality": "Old City (Charminar/Malakpet)",
        "longitude": 78.4747,
        "latitude": 17.3616,
        "bearing_capacity_kpa": 145.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 4.5,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Filled / residual red soil",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Banjara Hills/Jubilee Hills",
        "longitude": 78.4482,
        "latitude": 17.4156,
        "bearing_capacity_kpa": 320.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 18.0,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Rocky Deccan basalt",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Gachibowli/HITEC City",
        "longitude": 78.3489,
        "latitude": 17.4401,
        "bearing_capacity_kpa": 250.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 12.0,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Red Sandy Loam",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Kokapet/Narsingi",
        "longitude": 78.3340,
        "latitude": 17.3850,
        "bearing_capacity_kpa": 210.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 9.5,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Transitional red soil",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Gandipet/Manikonda",
        "longitude": 78.3200,
        "latitude": 17.3800,
        "bearing_capacity_kpa": 120.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 2.8,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Alluvial / lacustrine",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Kompally/Medchal",
        "longitude": 78.4850,
        "latitude": 17.5400,
        "bearing_capacity_kpa": 200.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 10.0,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Flat residual red soil",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Uppal/LB Nagar",
        "longitude": 78.5580,
        "latitude": 17.3980,
        "bearing_capacity_kpa": 180.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 7.5,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Mixed residual soil",  # ESTIMATED_DEMO_VALUES
    },
    {
        "locality": "Shamshabad",
        "longitude": 78.4294,
        "latitude": 17.2403,
        "bearing_capacity_kpa": 230.0,  # ESTIMATED_DEMO_VALUES
        "water_table_depth_m": 11.0,  # ESTIMATED_DEMO_VALUES
        "soil_type": "Weathered granite / red soil",  # ESTIMATED_DEMO_VALUES
    },
]

HYDERABAD_BBOX = {
    "min_lon": 78.15,
    "max_lon": 78.70,
    "min_lat": 17.15,
    "max_lat": 17.65,
}

DEFAULT_DEMO_LOCALITY = "Gachibowli/HITEC City"
