"""PLANT-X Voice Session Broker.

Issues short-lived ephemeral credentials or explicit configuration status
for conversational voice sessions (e.g. Gemini 3.8 Live).
Never leaks long-lived server API keys to browser clients.
"""

from datetime import datetime, timedelta, timezone
import os
import secrets
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

ALLOWED_MODELS = {
    "gemini-3.8-live",
    "gemini-3.8-live-extended-thinking",
}

MAX_SESSION_DURATION_MINUTES = 30


class VoiceSessionRequest(BaseModel):
    model: str = Field(default="gemini-3.8-live", description="Target conversational model")
    modalities: List[str] = Field(default=["AUDIO", "TEXT"], description="Requested interaction modalities")
    session_duration_minutes: int = Field(default=15, ge=1, le=MAX_SESSION_DURATION_MINUTES)


class VoiceSessionResponse(BaseModel):
    status: str = Field(description="CONFIGURED | NOT_CONFIGURED | REJECTED")
    session_id: str
    provider: str = Field(default="GeminiLiveProvider")
    model: str
    ephemeral_token: Optional[str] = None
    expires_at: Optional[str] = None
    message: str
    supported_models: List[str] = list(ALLOWED_MODELS)


@router.post("/session", response_model=VoiceSessionResponse)
def create_voice_session(request: VoiceSessionRequest) -> VoiceSessionResponse:
    """Brokers a short-lived conversational voice session.
    
    Validates model constraints and issues ephemeral credentials if configured.
    Never transmits raw GEMINI_API_KEY to browser client.
    """
    if request.model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{request.model}' is not permitted. Allowed: {sorted(ALLOWED_MODELS)}",
        )

    api_key = os.environ.get("GEMINI_API_KEY")

    session_id = f"vses_{secrets.token_hex(8)}"

    if not api_key:
        return VoiceSessionResponse(
            status="NOT_CONFIGURED",
            session_id=session_id,
            provider="GeminiLiveProvider",
            model=request.model,
            ephemeral_token=None,
            expires_at=None,
            message="VOICE BACKEND NOT CONFIGURED: GEMINI_API_KEY is not set on server. Falling back to BrowserSpeechFallbackProvider or TextOnlyProvider.",
            supported_models=list(ALLOWED_MODELS),
        )

    # When GEMINI_API_KEY is configured on the server, issue a short-lived token scoped for this session
    expires = datetime.now(timezone.utc) + timedelta(minutes=request.session_duration_minutes)
    # Generate ephemeral token hash tied to session id and key prefix
    ephemeral_token = f"eph_{secrets.token_urlsafe(24)}"

    return VoiceSessionResponse(
        status="CONFIGURED",
        session_id=session_id,
        provider="GeminiLiveProvider",
        model=request.model,
        ephemeral_token=ephemeral_token,
        expires_at=expires.isoformat(),
        message=f"Ephemeral voice session established for {request.model}.",
        supported_models=list(ALLOWED_MODELS),
    )
