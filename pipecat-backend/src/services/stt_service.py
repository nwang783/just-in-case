"""
Speech-to-Text (STT) service integration.
Supports multiple providers with easy swapping via factory pattern.
"""

from typing import Optional
from loguru import logger

# Pipecat STT integrations
from pipecat.services.deepgram.stt import DeepgramSTTService

# Azure STT is optional - only import if needed
AzureSTTService = None

from src.config.settings import Settings


class STTServiceFactory:
    """Factory for creating STT service instances."""

    @staticmethod
    def create_deepgram_stt(settings: Settings) -> DeepgramSTTService:
        """
        Create a Deepgram STT service.

        Args:
            settings: Application settings

        Returns:
            Configured Deepgram STT service
        """
        logger.info("Creating Deepgram STT service")

        return DeepgramSTTService(
            api_key=settings.deepgram_api_key,
        )

    @staticmethod
    def create_azure_stt(settings: Settings) -> Optional[object]:
        """
        Create an Azure STT service.

        Args:
            settings: Application settings

        Returns:
            Configured Azure STT service or None if not available
        """
        global AzureSTTService

        # Lazy import to avoid errors if not installed
        if AzureSTTService is None:
            try:
                from pipecat.services.azure.stt import AzureSTTService as AzSTT
                AzureSTTService = AzSTT
            except (ImportError, Exception):
                logger.error("Azure STT service not available. Install with: pip install pipecat-ai[azure]")
                return None

        logger.info("Creating Azure STT service")
        # Note: Azure STT requires additional configuration
        # This is a placeholder for when Azure is needed
        logger.warning("Azure STT service requires additional configuration")
        return None

    @staticmethod
    def create_stt(
        settings: Settings,
        provider: str = "deepgram"
    ) -> object:
        """
        Create an STT service based on the specified provider.

        Args:
            settings: Application settings
            provider: STT provider name ("deepgram" or "azure")

        Returns:
            Configured STT service

        Raises:
            ValueError: If provider is not supported
        """
        providers = {
            "deepgram": STTServiceFactory.create_deepgram_stt,
            "azure": STTServiceFactory.create_azure_stt,
        }

        factory_func = providers.get(provider.lower())
        if not factory_func:
            raise ValueError(
                f"Unsupported STT provider: {provider}. "
                f"Supported providers: {', '.join(providers.keys())}"
            )

        service = factory_func(settings)
        if service is None:
            raise RuntimeError(f"Failed to create {provider} STT service")

        return service
