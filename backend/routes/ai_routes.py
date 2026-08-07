"""AI advisor + chat for arbitrary map clicks."""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, HTTPException, Request

from models.ai_schemas import (
    AdvisorRequest,
    AIAdvisorResponse,
    ChatRequest,
    ChatResponse,
)
from services.ai_fallback_service import get_ai_chat_safe, get_ai_summary_safe
from services.ai_prompt_service import VALID_ROLES, normalize_role
from services.geo_validation import validate_hyderabad_coords
from services.location_context_service import assemble_location_context
from services.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["ai"])

MAX_CHAT_MESSAGE_LEN = 500
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.I),
    re.compile(r"ignore\s+all\s+prior\s+instructions", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|prompts)", re.I),
    re.compile(r"forget\s+(all\s+)?(previous|prior)\s+instructions", re.I),
]


def _validate_role(role: str) -> str:
    normalized = normalize_role(role)
    if normalized not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Use builder, investor, or homebuyer.",
        )
    return normalized


def _reject_injection(message: str) -> None:
    if len(message) > MAX_CHAT_MESSAGE_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long (max {MAX_CHAT_MESSAGE_LEN} characters)",
        )
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(message):
            raise HTTPException(status_code=400, detail="Message rejected")


@router.post("/ai-advisor", response_model=AIAdvisorResponse)
@limiter.limit("8/minute")
def ai_advisor(request: Request, payload: AdvisorRequest):
    _ = request
    role = _validate_role(payload.role)
    validate_hyderabad_coords(longitude=payload.longitude, latitude=payload.latitude)

    context = assemble_location_context(
        longitude=payload.longitude,
        latitude=payload.latitude,
        locality_name=payload.locality_name,
    )
    result = get_ai_summary_safe(
        longitude=payload.longitude,
        latitude=payload.latitude,
        role=role,
        context=context,
    )
    plot_id = None
    if isinstance(context.get("core"), dict):
        plot_id = context["core"].get("plot_id")
    elif isinstance(context.get("location"), dict):
        plot_id = context["location"].get("plot_id")

    return AIAdvisorResponse(
        plot_id=plot_id,
        role=role,
        summary_points=list(result["summary_points"])[:3],
        suggested_questions=list(result["suggested_questions"])[:3],
    )


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, payload: ChatRequest):
    _ = request
    role = _validate_role(payload.role)
    validate_hyderabad_coords(longitude=payload.longitude, latitude=payload.latitude)
    _reject_injection(payload.message.strip())

    context = assemble_location_context(
        longitude=payload.longitude,
        latitude=payload.latitude,
        locality_name=payload.locality_name,
    )
    answer = get_ai_chat_safe(
        longitude=payload.longitude,
        latitude=payload.latitude,
        role=role,
        context=context,
        message=payload.message.strip(),
        conversation_history=payload.conversation_history,
    )
    return ChatResponse(role=role, answer=answer)
