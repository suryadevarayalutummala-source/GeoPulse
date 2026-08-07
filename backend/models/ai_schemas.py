from pydantic import BaseModel, Field


class AIAdvisorResponse(BaseModel):
    plot_id: str | None = None
    role: str
    summary_points: list[str] = Field(..., min_length=3, max_length=3)
    suggested_questions: list[str] = Field(..., min_length=3, max_length=3)


class AdvisorLLMPayload(BaseModel):
    """Slim schema for Gemini structured output."""

    summary_points: list[str] = Field(..., min_length=3, max_length=3)
    suggested_questions: list[str] = Field(..., min_length=3, max_length=3)


class AnalyzeLocationRequest(BaseModel):
    # Field order matches team convention: longitude, then latitude (GeoJSON-style).
    longitude: float
    latitude: float
    locality_name: str | None = None


class AdvisorRequest(BaseModel):
    longitude: float
    latitude: float
    role: str
    locality_name: str | None = None


class ChatRequest(BaseModel):
    longitude: float
    latitude: float
    role: str
    message: str
    conversation_history: list[dict] | None = None
    locality_name: str | None = None


class ChatResponse(BaseModel):
    role: str
    answer: str
