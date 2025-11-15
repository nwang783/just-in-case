"""
Utilities for managing Daily.co rooms.
Handles creation of short-lived rooms on demand for each bot session.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests
from loguru import logger

from src.config.settings import Settings


class DailyRoomCreationError(RuntimeError):
    """Raised when the Daily API cannot create a room."""


@dataclass
class DailyRoom:
    """Represents a Daily room that was created programmatically."""

    name: str
    url: str
    expires_at: Optional[int]

    def pretty_expiration(self) -> str:
        """Return a human-readable expiration timestamp."""
        if not self.expires_at:
            return "Never"
        dt = datetime.fromtimestamp(self.expires_at, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


class DailyRoomService:
    """Service wrapper around the Daily REST API."""

    DAILY_ROOMS_ENDPOINT = "https://api.daily.co/v1/rooms"

    def __init__(self, settings: Settings):
        self.settings = settings

    def create_room(self) -> DailyRoom:
        """Create a Daily room using configuration defaults."""
        room_name = self._generate_room_name()
        expiration_ts = self._calculate_expiration()

        payload = {"name": room_name}
        if expiration_ts:
            payload["properties"] = {"exp": expiration_ts}

        logger.info(f"Creating Daily room '{room_name}'")

        room_data = self._perform_request(payload)

        return DailyRoom(
            name=room_data["name"],
            url=room_data["url"],
            expires_at=room_data.get("config", {}).get("exp"),
        )

    def _generate_room_name(self) -> str:
        """Generate a unique, shareable room name."""
        prefix = (self.settings.daily_room_prefix or "case-coach").strip()
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        suffix = secrets.token_hex(2)
        return f"{prefix}-{timestamp}-{suffix}"

    def _calculate_expiration(self) -> Optional[int]:
        """Return expiration timestamp in seconds since epoch."""
        minutes = self.settings.daily_room_exp_minutes
        if minutes and minutes > 0:
            return int(time.time()) + (minutes * 60)
        return None

    def _perform_request(self, payload: dict) -> dict:
        """Execute the POST request to Daily with error handling."""
        headers = {
            "Authorization": f"Bearer {self.settings.daily_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.DAILY_ROOMS_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to create Daily room via API", exc_info=True)
            raise DailyRoomCreationError(str(exc)) from exc

        return response.json()

    @classmethod
    def create_room_with_api_key(
        cls,
        api_key: str,
        room_name: Optional[str] = None,
        exp_time: Optional[int] = None,
    ) -> dict:
        """
        Backwards-compatible helper that mirrors the previous factory method.

        Args:
            api_key: Daily API key
            room_name: Desired room name
            exp_time: Expiration timestamp (seconds since epoch)
        """
        payload = {}
        if room_name:
            payload["name"] = room_name
        if exp_time:
            payload["properties"] = {"exp": exp_time}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            cls.DAILY_ROOMS_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
