"""
Daily.co WebRTC transport layer for Pipecat.
Handles real-time audio/video streaming via Daily.co infrastructure.
"""

from typing import Optional
from loguru import logger
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.audio.vad.silero import SileroVADAnalyzer

from src.config.settings import Settings
from src.services.daily_room_service import DailyRoomService


class DailyTransportFactory:
    """Factory for creating Daily.co transport instances."""

    @staticmethod
    def create_transport(
        settings: Settings,
        room_url: Optional[str] = None,
        token: Optional[str] = None,
        bot_name: Optional[str] = None,
        audio_out_enabled: bool = True,
        audio_in_enabled: bool = True,
        video_out_enabled: bool = False,
        video_in_enabled: bool = False,
        transcription_enabled: bool = False,
        vad_analyzer: Optional[SileroVADAnalyzer] = None,
        turn_analyzer: Optional[object] = None,
    ) -> DailyTransport:
        """
        Create a Daily.co transport instance.

        Args:
            settings: Application settings
            room_url: Daily.co room URL (overrides settings)
            token: Daily.co meeting token (optional)
            bot_name: Bot display name (overrides settings)
            audio_out_enabled: Enable audio output (TTS)
            audio_in_enabled: Enable audio input (STT)
            video_out_enabled: Enable video output
            video_in_enabled: Enable video input
            transcription_enabled: Enable Daily transcription
            vad_analyzer: Optional VAD analyzer for speech detection
            turn_analyzer: Optional turn analyzer for conversation turn detection

        Returns:
            Configured DailyTransport instance
        """
        # Use provided values or fall back to settings
        final_room_url = room_url or settings.daily_room_url
        final_bot_name = bot_name or settings.bot_name

        if not final_room_url:
            raise ValueError(
                "Daily room URL must be provided either via parameter or DAILY_ROOM_URL env variable"
            )

        logger.info(f"Creating Daily transport for room: {final_room_url}")
        logger.info(f"Bot name: {final_bot_name}")
        logger.info(
            f"Audio in/out: {audio_in_enabled}/{audio_out_enabled}, "
            f"Video in/out: {video_in_enabled}/{video_out_enabled}"
        )

        if vad_analyzer:
            logger.info("VAD analyzer configured for transport")
        if turn_analyzer:
            logger.info("Turn analyzer configured for transport")

        # Configure Daily parameters
        params = DailyParams(
            audio_out_enabled=audio_out_enabled,
            audio_in_enabled=audio_in_enabled,
            video_out_enabled=video_out_enabled,
            video_in_enabled=video_in_enabled,
            transcription_enabled=transcription_enabled,
            vad_analyzer=vad_analyzer,
            turn_analyzer=turn_analyzer,
        )

        # Create and return transport
        transport = DailyTransport(
            room_url=final_room_url,
            token=token or "",  # Empty string if no token
            bot_name=final_bot_name,
            params=params,
        )

        return transport

    @staticmethod
    def create_room(
        api_key: str,
        room_name: Optional[str] = None,
        exp_time: Optional[int] = None
    ) -> dict:
        """
        Create a new Daily.co room programmatically.

        Args:
            api_key: Daily.co API key
            room_name: Optional room name (auto-generated if not provided)
            exp_time: Room expiration time in seconds from now

        Returns:
            Room information dictionary

        Note:
            This requires the 'requests' package and Daily.co API access
        """
        room_data = DailyRoomService.create_room_with_api_key(
            api_key=api_key,
            room_name=room_name,
            exp_time=exp_time,
        )
        logger.info(f"Room created: {room_data['url']}")
        return room_data
