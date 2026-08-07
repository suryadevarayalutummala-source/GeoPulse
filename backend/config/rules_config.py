"""
Central Hyderabad regulatory rules — update numbers here without touching service logic.

Sources (demo): HYDRAA FTL buffer practice, GO 111 catchment protection,
and known HYDRAA enforcement-drive localities. Not legal advice.
"""

from __future__ import annotations

HYDERABAD_REGULATORY_RULES: dict = {
    # Lakes > 10 hectares (HYDRAA Full Tank Level buffer)
    "LAKE_BUFFER_MAJOR_METERS": 30.0,
    # Lakes < 10 hectares or major nalas
    "LAKE_BUFFER_MINOR_METERS": 9.0,
    "GO_111_LAKES": [
        {"name": "Osman Sagar", "lat": 17.3800, "lon": 78.2933},
        {"name": "Himayat Sagar", "lat": 17.3200, "lon": 78.3580},
    ],
    "GO_111_RADIUS_KM": 10.0,
    "ACTIVE_HYDRAA_DRIVE_ZONES": [
        "Ameenpur",
        "Nizampet",
        "Gachibowli",
        "Manikonda",
        "Kukatpally",
        "Chandanagar",
    ],
    # Retroactive policy adaptation (historical vs current)
    # If a structure would have been legal under HISTORICAL but illegal under CURRENT → flag.
    "HISTORICAL_LAKE_BUFFER_MAJOR_METERS": 9.0,
    "CURRENT_LAKE_BUFFER_MAJOR_METERS": 30.0,
}
