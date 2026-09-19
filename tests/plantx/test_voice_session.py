"""Unit tests for Secure Voice Session Broker."""

import os
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from src.plantx.voice.session import (
    create_voice_session,
    VoiceSessionRequest,
    VoiceSessionResponse,
)


def test_voice_session_not_configured():
    """Verify that when GEMINI_API_KEY is not set, status is NOT_CONFIGURED and no token leaks."""
    with patch.dict(os.environ, {}, clear=True):
        req = VoiceSessionRequest(model="gemini-3.8-live")
        res = create_voice_session(req)
        assert res.status == "NOT_CONFIGURED"
        assert res.ephemeral_token is None
        assert "VOICE BACKEND NOT CONFIGURED" in res.message
        assert res.model == "gemini-3.8-live"


def test_voice_session_configured():
    """Verify that when GEMINI_API_KEY is present, ephemeral token is issued with expiry."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSyFakeKeyForTest1234567890"}):
        req = VoiceSessionRequest(
            model="gemini-3.8-live-extended-thinking",
            session_duration_minutes=20,
        )
        res = create_voice_session(req)
        assert res.status == "CONFIGURED"
        assert res.ephemeral_token is not None
        assert res.ephemeral_token.startswith("eph_")
        assert res.session_id.startswith("vses_")
        assert res.model == "gemini-3.8-live-extended-thinking"
        assert res.expires_at is not None
        # Ensure server API key was NOT sent
        assert "AIzaSyFakeKeyForTest" not in str(res.model_dump())


def test_voice_session_invalid_model_rejected():
    """Verify that unauthorized models are rejected with 400 Bad Request."""
    req = VoiceSessionRequest(model="unsupported-model-v1")
    with pytest.raises(HTTPException) as exc_info:
        create_voice_session(req)
    assert exc_info.value.status_code == 400
    assert "not permitted" in exc_info.value.detail


def test_voice_session_duration_boundary():
    """Verify that session duration cannot exceed 30 minutes via Pydantic validation."""
    with pytest.raises(ValidationError):
        VoiceSessionRequest(session_duration_minutes=60)
