"""
Text-to-Speech (TTS) service integration.
Supports multiple providers with easy swapping via factory pattern.
"""

from typing import Optional
from loguru import logger

# Pipecat TTS integrations
from pipecat.services.openai.tts import OpenAITTSService

# ElevenLabs TTS is optional - only import if needed
ElevenLabsTTSService = None

# Cartesia TTS is optional - only import if needed
CartesiaTTSService = None

from src.config.settings import Settings


class TTSServiceFactory:
    """Factory for creating TTS service instances."""

    @staticmethod
    def create_openai_tts(settings: Settings, voice: str = "alloy") -> OpenAITTSService:
        """
        Create an OpenAI TTS service.

        Args:
            settings: Application settings
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            Configured OpenAI TTS service
        """
        logger.info(f"Creating OpenAI TTS service with voice: {voice}")

        return OpenAITTSService(
            api_key=settings.openai_api_key,
            voice=voice,
        )

    @staticmethod
    def create_elevenlabs_tts(settings: Settings) -> Optional[object]:
        """
        Create an ElevenLabs TTS service.

        Args:
            settings: Application settings

        Returns:
            Configured ElevenLabs TTS service or None if not available
        """
        global ElevenLabsTTSService

        # Lazy import to avoid errors if not installed
        if ElevenLabsTTSService is None:
            try:
                from pipecat.services.elevenlabs.tts import ElevenLabsTTSService as ELTTS
                ElevenLabsTTSService = ELTTS
            except (ImportError, Exception):
                logger.error("ElevenLabs service not available. Install with: pip install pipecat-ai[elevenlabs]")
                return None

        if not settings.elevenlabs_api_key:
            logger.error("ElevenLabs API key not configured")
            return None

        if not settings.elevenlabs_voice_id:
            logger.error("ElevenLabs voice ID not configured")
            return None

        logger.info(f"Creating ElevenLabs TTS service with voice ID: {settings.elevenlabs_voice_id}")

        return ElevenLabsTTSService(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
        )

    @staticmethod
    def create_cartesia_tts(settings: Settings) -> Optional[object]:
        """
        Create a Cartesia TTS service (WebSocket-based for real-time streaming).

        Args:
            settings: Application settings

        Returns:
            Configured Cartesia TTS service or None if not available
        """
        global CartesiaTTSService

        # Lazy import to avoid errors if not installed
        if CartesiaTTSService is None:
            try:
                from pipecat.services.cartesia import CartesiaTTSService as CTTS
                CartesiaTTSService = CTTS
            except (ImportError, Exception):
                logger.error("Cartesia service not available. Install with: pip install pipecat-ai[cartesia]")
                return None

        if not settings.cartesia_api_key:
            logger.error("Cartesia API key not configured")
            return None

        logger.info(
            f"Creating Cartesia TTS service with voice ID: {settings.cartesia_voice_id}, "
            f"model: {settings.cartesia_model}"
        )

        return CartesiaTTSService(
            api_key=settings.cartesia_api_key,
            voice_id=settings.cartesia_voice_id,
            model=settings.cartesia_model,
        )

    @staticmethod
    def create_tts(
        settings: Settings,
        provider: str = "openai",
        **kwargs
    ) -> object:
        """
        Create a TTS service based on the specified provider.

        Args:
            settings: Application settings
            provider: TTS provider name ("openai", "elevenlabs", or "cartesia")
            **kwargs: Additional provider-specific parameters

        Returns:
            Configured TTS service

        Raises:
            ValueError: If provider is not supported
        """
        if provider.lower() == "openai":
            voice = kwargs.get("voice", "alloy")
            return TTSServiceFactory.create_openai_tts(settings, voice)

        elif provider.lower() == "elevenlabs":
            service = TTSServiceFactory.create_elevenlabs_tts(settings)
            if service is None:
                raise RuntimeError("Failed to create ElevenLabs TTS service")
            return service

        elif provider.lower() == "cartesia":
            service = TTSServiceFactory.create_cartesia_tts(settings)
            if service is None:
                raise RuntimeError("Failed to create Cartesia TTS service")
            return service

        else:
            raise ValueError(
                f"Unsupported TTS provider: {provider}. "
                f"Supported providers: openai, elevenlabs, cartesia"
            )
