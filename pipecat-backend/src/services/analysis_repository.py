"""
Read structured transcript analysis files and expose API-friendly models.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Literal

from loguru import logger
from pydantic import BaseModel, ValidationError, Field

from src.services.transcript_analysis_service import TranscriptAnalysisResult


class TranscriptAnalysisPayload(TranscriptAnalysisResult):
    """Stored analysis payload persisted to disk."""

    source_transcript: str = Field(..., description="Filesystem path to the transcript used")


class AnalysisStatus(BaseModel):
    """Status wrapper returned to clients."""

    conversation_id: str
    status: Literal["pending", "ready"]
    updated_at: datetime
    analysis: Optional[TranscriptAnalysisPayload] = None


class AnalysisRepository:
    """Utility class for reading structured analyses from disk."""

    def __init__(self, transcripts_dir: Path, analysis_dir: Path) -> None:
        self.transcripts_dir = Path(transcripts_dir)
        self.analysis_dir = Path(analysis_dir)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

    def list_analyses(self, limit: int = 20, include_pending: bool = False) -> List[AnalysisStatus]:
        """
        Return the latest analyses sorted by update time.

        When include_pending is True, transcripts that have not finished analysis
        are also included in the response.
        """
        limit = max(1, min(limit, 100))
        statuses: List[AnalysisStatus] = []

        for path in self.analysis_dir.glob("*-analysis.json"):
            status = self._status_from_analysis_file(path)
            if status:
                statuses.append(status)

        if include_pending:
            for path in self.transcripts_dir.glob("conversation-*.jsonl"):
                conversation_id = path.stem
                if any(entry.conversation_id == conversation_id for entry in statuses):
                    continue
                if self._analysis_path(conversation_id).exists():
                    continue
                updated_at = self._timestamp_to_datetime(path.stat().st_mtime)
                statuses.append(
                    AnalysisStatus(
                        conversation_id=conversation_id,
                        status="pending",
                        updated_at=updated_at,
                    )
                )

        statuses.sort(key=lambda item: item.updated_at, reverse=True)
        return statuses[:limit]

    def get_status(self, conversation_id: str) -> Optional[AnalysisStatus]:
        """
        Return the analysis status for a given conversation.

        If the transcript exists but the analysis is not yet written, returns a
        pending status. Otherwise returns ready or None if nothing is available.
        """
        analysis_path = self._analysis_path(conversation_id)
        if analysis_path.exists():
            return self._status_from_analysis_file(analysis_path)

        transcript_path = self._transcript_path(conversation_id)
        if transcript_path.exists():
            updated_at = self._timestamp_to_datetime(transcript_path.stat().st_mtime)
            return AnalysisStatus(
                conversation_id=conversation_id,
                status="pending",
                updated_at=updated_at,
            )
        return None

    def _status_from_analysis_file(self, path: Path) -> Optional[AnalysisStatus]:
        payload = self._load_analysis_payload(path)
        if not payload:
            return None
        updated_at = self._timestamp_to_datetime(path.stat().st_mtime)
        return AnalysisStatus(
            conversation_id=payload.conversation_id,
            status="ready",
            updated_at=updated_at,
            analysis=payload,
        )

    def _load_analysis_payload(self, path: Path) -> Optional[TranscriptAnalysisPayload]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            logger.error(f"Failed reading analysis file {path}: {exc}")
            return None
        except json.JSONDecodeError as exc:
            logger.error(f"Malformed analysis JSON {path}: {exc}")
            return None

        try:
            return TranscriptAnalysisPayload.model_validate(data)
        except ValidationError as exc:
            logger.error(f"Analysis JSON did not match schema ({path}): {exc}")
            return None

    def _transcript_path(self, conversation_id: str) -> Path:
        return self.transcripts_dir / f"{conversation_id}.jsonl"

    def _analysis_path(self, conversation_id: str) -> Path:
        return self.analysis_dir / f"{conversation_id}-analysis.json"

    @staticmethod
    def _timestamp_to_datetime(value: float) -> datetime:
        return datetime.fromtimestamp(value, tz=timezone.utc)
