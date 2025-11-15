"""
Service utilities for persisting conversation transcripts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Literal, Optional
from uuid import uuid4

from loguru import logger


class TranscriptWriter:
    """
    Persist conversation transcripts as structured JSONL files.

    Files are written incrementally so that transcripts survive crashes
    and can be tailed or analyzed in real time.
    """

    def __init__(
        self,
        output_dir: Path,
        room_url: Optional[str] = None,
        bot_name: Optional[str] = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc)
        slug = timestamp.strftime("%Y%m%d-%H%M%S")
        suffix = uuid4().hex[:8]
        self.conversation_id = f"conversation-{slug}-{suffix}"
        self.file_path = self.output_dir / f"{self.conversation_id}.jsonl"
        self.started_at = timestamp
        self.room_url = room_url
        self.bot_name = bot_name
        self._lock = Lock()

        logger.info(f"Transcripts will be saved to: {self.file_path}")
        self._write_line(
            {
                "type": "metadata",
                "conversation_id": self.conversation_id,
                "started_at": self.started_at.isoformat(),
                "room_url": self.room_url,
                "bot_name": self.bot_name,
            }
        )

    def _write_line(self, payload: dict) -> None:
        """Write a JSON payload to the transcript file."""
        with self._lock:
            with self.file_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def record_message(
        self,
        role: Literal["user", "assistant"],
        text: str,
        extra: Optional[dict] = None,
    ) -> None:
        """Append a message entry to the transcript."""
        if not text:
            return

        entry = {
            "type": "message",
            "conversation_id": self.conversation_id,
            "role": role,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if extra:
            entry["metadata"] = extra

        self._write_line(entry)

    def mark_conversation_end(self, reason: str = "completed") -> None:
        """Record that the conversation has ended."""
        self._write_line(
            {
                "type": "conversation_end",
                "conversation_id": self.conversation_id,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            }
        )
