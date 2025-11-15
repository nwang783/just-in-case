"""
In-memory session manager for orchestrating interview sessions.

Each session represents a Daily room and an optional running VoiceAgent instance.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from loguru import logger

from src.bot.voice_agent import VoiceAgent
from src.config.settings import Settings
from src.services.daily_room_service import DailyRoom, DailyRoomCreationError, DailyRoomService
from src.config.interview_prompts import build_interview_prompt

# Session status constants
SESSION_ROOM_CREATED = "room_created"
SESSION_BOT_STARTING = "bot_starting"
SESSION_BOT_RUNNING = "bot_running"
SESSION_BOT_STOPPING = "bot_stopping"
SESSION_BOT_COMPLETED = "bot_completed"
SESSION_BOT_ERROR = "bot_error"


class SessionNotFoundError(KeyError):
    """Raised when attempting to access a non-existent session."""


class SessionStateError(RuntimeError):
    """Raised when an operation is not allowed in the current session state."""


@dataclass
class SessionRecord:
    """Represents a single interview session."""

    session_id: str
    company_slug: str
    interview_type: str
    room_url: str
    room_name: str
    expires_at: Optional[int]
    status: str = SESSION_ROOM_CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_error: Optional[str] = None
    session_prompt: Optional[str] = None
    bot_task: Optional[asyncio.Task] = field(default=None, repr=False)
    voice_agent: Optional[VoiceAgent] = field(default=None, repr=False)
    conversation_id: Optional[str] = None
    transcript_path: Optional[str] = None
    analysis_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Serialize the record for API responses."""
        return {
            "sessionId": self.session_id,
            "companySlug": self.company_slug,
            "interviewType": self.interview_type,
            "roomUrl": self.room_url,
            "roomName": self.room_name,
            "expiresAt": self.expires_at,
            "status": self.status,
            "lastError": self.last_error,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "conversationId": self.conversation_id,
            "transcriptPath": self.transcript_path,
            "analysisPath": self.analysis_path,
        }


class SessionManager:
    """Coordinates Daily room creation and VoiceAgent lifecycle."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.room_service = DailyRoomService(settings)
        self._sessions: Dict[str, SessionRecord] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, *, company_slug: str, interview_type: str) -> SessionRecord:
        """Create a new Daily room and track a session."""
        try:
            daily_room: DailyRoom = await asyncio.to_thread(self.room_service.create_room)
        except DailyRoomCreationError:
            raise
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Unexpected error while creating Daily room")
            raise DailyRoomCreationError(str(exc)) from exc

        session_id = str(uuid.uuid4())
        session = SessionRecord(
            session_id=session_id,
            company_slug=company_slug,
            interview_type=interview_type,
            room_url=daily_room.url,
            room_name=daily_room.name,
            expires_at=daily_room.expires_at,
            session_prompt=build_interview_prompt(company_slug, interview_type),
        )

        async with self._lock:
            self._sessions[session_id] = session

        logger.info(f"Created session {session_id} for {company_slug} ({interview_type})")
        return session

    async def get_session(self, session_id: str) -> SessionRecord:
        """Return a session by id."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(session_id)
            return session

    async def start_bot(self, session_id: str) -> SessionRecord:
        """Launch the VoiceAgent for a session."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(session_id)
            if session.bot_task and not session.bot_task.done():
                raise SessionStateError("Voice agent already running for this session")

            voice_agent = VoiceAgent(
                settings=self.settings,
                room_url=session.room_url,
                session_prompt=session.session_prompt,
            )
            session.voice_agent = voice_agent
            session.status = SESSION_BOT_STARTING
            session.last_error = None
            session.updated_at = datetime.now(timezone.utc)

            session.bot_task = asyncio.create_task(self._run_session(session_id, voice_agent))

            logger.info(f"Starting voice agent for session {session_id}")
            return session

    async def stop_session(self, session_id: str) -> SessionRecord:
        """Request the running VoiceAgent to stop."""
        session = await self.get_session(session_id)

        if not session.bot_task or session.bot_task.done():
            return session

        await self._update_session_status(session_id, SESSION_BOT_STOPPING)

        if session.voice_agent:
            await session.voice_agent.stop()

        try:
            await session.bot_task
        except Exception as exc:  # pragma: no cover - logging/cleanup
            logger.error(f"Voice agent stop failed for session {session_id}: {exc}", exc_info=True)
            await self._update_session_status(session_id, SESSION_BOT_ERROR, error=str(exc))
        finally:
            await self._clear_agent(session_id)

        return await self.get_session(session_id)

    async def list_sessions(self) -> Dict[str, SessionRecord]:
        """Return a snapshot of known sessions."""
        async with self._lock:
            return dict(self._sessions)

    async def _run_session(self, session_id: str, agent: VoiceAgent) -> None:
        """Run the VoiceAgent and keep status in sync."""
        await self._update_session_status(session_id, SESSION_BOT_RUNNING)
        try:
            await agent.run()
            await self._update_session_status(session_id, SESSION_BOT_COMPLETED)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"Voice agent error for session {session_id}: {exc}", exc_info=True)
            await self._update_session_status(session_id, SESSION_BOT_ERROR, error=str(exc))
        finally:
            await self._clear_agent(session_id)

    async def _update_session_status(
        self,
        session_id: str,
        status: str,
        *,
        error: Optional[str] = None,
    ) -> None:
        """Update a session's status safely."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise SessionNotFoundError(session_id)
            session.status = status
            session.updated_at = datetime.now(timezone.utc)
            session.last_error = error

    async def _clear_agent(self, session_id: str) -> None:
        """Remove agent/task references after completion."""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return
            agent = session.voice_agent
            if agent and agent.transcript_writer:
                writer = agent.transcript_writer
                session.conversation_id = writer.conversation_id
                session.transcript_path = str(writer.file_path)
                analysis_path = (
                    self.settings.transcript_analysis_dir
                    / f"{writer.file_path.stem}-analysis.json"
                )
                session.analysis_path = str(analysis_path)
            session.bot_task = None
            session.voice_agent = None
