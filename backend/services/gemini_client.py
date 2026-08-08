"""Google Gemini client (google-genai SDK). API key via GEMINI_API_KEY only."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from google import genai
from google.genai import types

from models.ai_schemas import AdvisorLLMPayload
from services.ai_prompt_service import generate_chat_prompt, generate_role_prompt, normalize_role

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash-lite"


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    return genai.Client(api_key=api_key)


def call_gemini_for_summary(role: str, context: dict[str, Any]) -> dict[str, Any]:
    role = normalize_role(role)
    prompt = generate_role_prompt(role, context)
    client = _get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AdvisorLLMPayload,
            temperature=0.4,
        ),
    )

    raw = (response.text or "").strip()
    if not raw:
        raise RuntimeError("Empty Gemini response")

    data = json.loads(raw)
    parsed = AdvisorLLMPayload(
        summary_points=list(data["summary_points"])[:3],
        suggested_questions=list(data["suggested_questions"])[:3],
    )
    if len(parsed.summary_points) != 3 or len(parsed.suggested_questions) != 3:
        raise RuntimeError("Gemini returned incomplete advisor payload")

    return {
        "summary_points": parsed.summary_points,
        "suggested_questions": parsed.suggested_questions,
        "role": role,
    }


def call_gemini_for_chat(
    role: str,
    context: dict[str, Any],
    message: str,
    conversation_history: list[dict] | None = None,
) -> str:
    role = normalize_role(role)
    prompt = generate_chat_prompt(role, context, message, conversation_history)
    client = _get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.5),
    )
    answer = (response.text or "").strip()
    if not answer:
        raise RuntimeError("Empty Gemini chat response")
    return answer
