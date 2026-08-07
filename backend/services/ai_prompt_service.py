"""Role-specific prompts using finalized team field names."""

from __future__ import annotations

from typing import Any

VALID_ROLES = {"builder", "investor", "homebuyer"}


def normalize_role(role: str) -> str:
    r = (role or "").strip().lower()
    if r in ("homebuyer", "resident", "buyer"):
        return "homebuyer"
    if r in ("builder", "investor"):
        return r
    return r


def generate_role_prompt(role: str, context: dict[str, Any]) -> str:
    role = normalize_role(role)
    core = context.get("core") or {}
    builder = context.get("builder") or {}
    investor = context.get("investor") or {}
    buyer = context.get("buyer") or {}
    scores = context.get("scores") or {}
    place = (
        context.get("locality_name")
        or core.get("name")
        or "this Hyderabad location"
    )

    output_rules = """
Return ONLY valid JSON with exactly these keys:
- "summary_points": array of EXACTLY 3 concise, data-grounded bullet strings
- "suggested_questions": array of EXACTLY 3 questions
  - items 1 and 2 MUST reference this location's actual numbers for this role
  - item 3 MUST be a general question useful for anyone in this role
No intro, outro, or markdown fences.
""".strip()

    if role == "builder":
        return f"""You are a Senior Geotechnical Consultant for {place}.

Use these Builder + Core fields only:
- soil_type: {builder.get("soil_type")}
- bearing_capacity_kpa: {builder.get("bearing_capacity_kpa")}
- water_table_depth_m: {builder.get("water_table_depth_m")}
- flood_risk_zone: {builder.get("flood_risk_zone")}
- max_permissible_floors: {builder.get("max_permissible_floors")}
- utility_access: {builder.get("utility_access")}
- construction_cost_estimate_per_sqft: {builder.get("construction_cost_estimate_per_sqft")}
- zoning_type: {core.get("zoning_type")}
- area_sqft: {core.get("area_sqft")}
- estimation_note: {builder.get("estimation_note")}
- construction_score: {scores.get("construction_score")}

{output_rules}
""".strip()

    if role == "investor":
        return f"""You are a Real Estate Financial Analyst for {place}.

Use these Investor fields only:
- current_price_sqft: {investor.get("current_price_sqft")}
- historical_growth_rates: {investor.get("historical_growth_rates")}
- rental_yield_percentage: {investor.get("rental_yield_percentage")}
- roi_percentage: {investor.get("roi_percentage")}
- risk_score: {investor.get("risk_score")}
- infrastructure_development_pipeline: {investor.get("infrastructure_development_pipeline")}
- investment_score: {scores.get("investment_score")}

{output_rules}
""".strip()

    if role == "homebuyer":
        return f"""You are a Residential Livability Advisor helping a homebuyer evaluate {place}.

Use these Buyer fields only:
- schools_nearby: {buyer.get("schools_nearby")}
- hospitals_nearby: {buyer.get("hospitals_nearby")}
- transit_hubs_nearby: {buyer.get("transit_hubs_nearby")}
- nearest_hospital_km: {buyer.get("nearest_hospital_km")}
- air_quality_index: {buyer.get("air_quality_index")}
- commute_time_to_city_center_min: {buyer.get("commute_time_to_city_center_min")}
- livability_score: {scores.get("livability_score")}
- connectivity_score: {scores.get("connectivity_score")}

{output_rules}
""".strip()

    raise ValueError(f"Unsupported role: {role}")


def generate_chat_prompt(
    role: str,
    context: dict[str, Any],
    message: str,
    conversation_history: list[dict] | None = None,
) -> str:
    role = normalize_role(role)
    history_block = ""
    if conversation_history:
        lines = []
        for turn in conversation_history[-8:]:
            who = turn.get("role") or turn.get("speaker") or "user"
            text = turn.get("content") or turn.get("message") or ""
            lines.append(f"{who}: {text}")
        history_block = "Recent conversation:\n" + "\n".join(lines) + "\n\n"

    persona = {
        "builder": "Senior Geotechnical Consultant",
        "investor": "Real Estate Financial Analyst",
        "homebuyer": "Residential Livability Advisor",
    }.get(role, "Real Estate Advisor")

    # Pass only the finalized buckets into chat context
    slim = {
        "core": context.get("core"),
        "builder": context.get("builder"),
        "investor": context.get("investor"),
        "buyer": context.get("buyer"),
        "scores": context.get("scores"),
        "locality_name": context.get("locality_name"),
    }

    return f"""You are a {persona} for GeoPulse (Hyderabad).

Site context uses the team schema (core / builder / investor / buyer / scores):
{slim}

{history_block}User question: {message}

Answer in 2–4 short paragraphs. Ground claims in the context numbers.
For investment risk use investor.risk_score and scores.investment_score.
For construction risk use scores.construction_score and builder fields.
Do not invent regulations or prices absent from the context.
""".strip()
