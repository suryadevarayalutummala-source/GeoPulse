# GeoPulse Backend

## Key endpoint — map click analysis

`POST /api/v1/analyze-location`

```json
{ "lon": 78.3772, "lat": 17.4435, "locality": "optional" }
```

Runs concurrently (async):
- Overpass amenities + water bodies (`amenity_service`)
- IDW soil interpolation (`soil_interpolation_service`)
- Gemini Google Search market grounding (`market_grounding_service`)

Then fuses legal/environmental flags (`legal_risk_service`).

Response includes `legality_risk.map_buffers` for Mapbox 30m HYDRAA circles.

## Config
- `config/rules_config.py` — HYDRAA buffers, GO 111 lakes, drive zones
- `config/geo_reference_points.py` — IDW soil anchors (ESTIMATED_DEMO_VALUES)

## Env
`GEMINI_API_KEY` in `backend/.env`

## Run
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
