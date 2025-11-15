"""
FastAPI application exposing endpoints for managing interview sessions.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field, ConfigDict

from src.config.settings import settings
from src.services.daily_room_service import DailyRoomCreationError
from .session_manager import (
    SESSION_BOT_COMPLETED,
    SESSION_BOT_ERROR,
    SESSION_BOT_RUNNING,
    SESSION_BOT_STARTING,
    SESSION_BOT_STOPPING,
    SESSION_ROOM_CREATED,
    SessionManager,
    SessionNotFoundError,
    SessionRecord,
    SessionStateError,
)

ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
}

extra_origins = os.getenv("FRONTEND_ALLOWED_ORIGINS")
if extra_origins:
    for origin in extra_origins.split(","):
        origin = origin.strip()
        if origin:
            ALLOWED_ORIGINS.add(origin)

app = FastAPI(
    title="Case Interview Coach API",
    version="1.0.0",
    description="HTTP control plane for creating Daily rooms and orchestrating Pipecat voice agents.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager(settings=settings)


class CreateSessionRequest(BaseModel):
    """Payload for requesting a new interview session."""

    model_config = ConfigDict(extra="forbid")

    companySlug: str = Field(..., min_length=1, description="Identifier for the company page")
    interviewType: str = Field(..., min_length=1, description="Selected interview format")


class SessionResponse(BaseModel):
    """Standardized API response for a session."""

    sessionId: str
    companySlug: str
    interviewType: str
    roomUrl: str
    roomName: str
    expiresAt: Optional[int] = None
    status: str
    lastError: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def from_record(cls, record: SessionRecord) -> "SessionResponse":
        return cls(
            sessionId=record.session_id,
            companySlug=record.company_slug,
            interviewType=record.interview_type,
            roomUrl=record.room_url,
            roomName=record.room_name,
            expiresAt=record.expires_at,
            status=record.status,
            lastError=record.last_error,
            createdAt=record.created_at,
            updatedAt=record.updated_at,
        )


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Case Interview Coach API starting up")
    logger.info(f"Allowed CORS origins: {', '.join(sorted(ALLOWED_ORIGINS))}")


@app.get("/healthz")
async def healthcheck() -> dict:
    """Simple readiness check."""
    return {"status": "ok"}


@app.get("/api/sessions/statuses")
async def list_statuses() -> dict:
    """Expose allowed status values for client-side reference."""
    return {
        "statuses": [
            SESSION_ROOM_CREATED,
            SESSION_BOT_STARTING,
            SESSION_BOT_RUNNING,
            SESSION_BOT_STOPPING,
            SESSION_BOT_COMPLETED,
            SESSION_BOT_ERROR,
        ]
    }


@app.post("/api/sessions", response_model=SessionResponse, status_code=201)
async def create_session(payload: CreateSessionRequest) -> SessionResponse:
    """Create a Daily room for a selected interview."""
    try:
        session = await session_manager.create_session(
            company_slug=payload.companySlug,
            interview_type=payload.interviewType,
        )
    except DailyRoomCreationError as exc:
        logger.error(f"Daily room creation failed: {exc}")
        raise HTTPException(status_code=502, detail="Unable to create Daily room at this time") from exc

    return SessionResponse.from_record(session)


@app.get(
    "/api/sessions/{session_id}",
    response_model=SessionResponse,
)
async def get_session(
    session_id: str = Path(..., min_length=1, description="Session identifier returned from creation"),
) -> SessionResponse:
    """Retrieve session details and current status."""
    try:
        session = await session_manager.get_session(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    return SessionResponse.from_record(session)


@app.post(
    "/api/sessions/{session_id}/start",
    response_model=SessionResponse,
)
async def start_session(
    session_id: str = Path(..., min_length=1, description="Session identifier returned from creation"),
) -> SessionResponse:
    """Start the voice agent for a session. Assumes the candidate already joined the room."""
    try:
        session = await session_manager.start_bot(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except SessionStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return SessionResponse.from_record(session)


@app.post(
    "/api/sessions/{session_id}/stop",
    response_model=SessionResponse,
)
async def stop_session(
    session_id: str = Path(..., min_length=1, description="Session identifier returned from creation"),
) -> SessionResponse:
    """Gracefully stop the voice agent for a session."""
    try:
        await session_manager.stop_session(session_id)
        session = await session_manager.get_session(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc

    return SessionResponse.from_record(session)


@app.get(
    "/api/sessions",
    response_model=List[SessionResponse],
)
async def list_sessions() -> List[SessionResponse]:
    """Return all active sessions (useful for debugging)."""
    sessions = await session_manager.list_sessions()
    return [SessionResponse.from_record(record) for record in sessions.values()]

