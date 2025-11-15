"""
Large Language Model (LLM) service integration.
Supports multiple providers with easy swapping via factory pattern.
"""

from typing import Optional
from loguru import logger

# Pipecat LLM integrations
from pipecat.services.openai.llm import OpenAILLMService

# Anthropic LLM is optional - only import if needed
AnthropicLLMService = None

from src.config.settings import Settings


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    @staticmethod
    def create_openai_llm(settings: Settings) -> OpenAILLMService:
        """
        Create an OpenAI LLM service.

        Args:
            settings: Application settings

        Returns:
            Configured OpenAI LLM service
        """
        logger.info(f"Creating OpenAI LLM service with model: {settings.openai_model}")

        return OpenAILLMService(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    @staticmethod
    def create_anthropic_llm(settings: Settings) -> Optional[object]:
        """
        Create an Anthropic Claude LLM service.

        Args:
            settings: Application settings

        Returns:
            Configured Anthropic LLM service or None if not available
        """
        global AnthropicLLMService

        # Lazy import to avoid errors if not installed
        if AnthropicLLMService is None:
            try:
                from pipecat.services.anthropic.llm import AnthropicLLMService as AntLLM
                AnthropicLLMService = AntLLM
            except (ImportError, Exception):
                logger.error("Anthropic service not available. Install with: pip install pipecat-ai[anthropic]")
                return None

        if not settings.anthropic_api_key:
            logger.error("Anthropic API key not configured")
            return None

        logger.info(f"Creating Anthropic LLM service with model: {settings.anthropic_model}")

        return AnthropicLLMService(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )

    @staticmethod
    def create_llm(
        settings: Settings,
        provider: str = "openai"
    ) -> object:
        """
        Create an LLM service based on the specified provider.

        Args:
            settings: Application settings
            provider: LLM provider name ("openai" or "anthropic")

        Returns:
            Configured LLM service

        Raises:
            ValueError: If provider is not supported
        """
        providers = {
            "openai": LLMServiceFactory.create_openai_llm,
            "anthropic": LLMServiceFactory.create_anthropic_llm,
        }

        factory_func = providers.get(provider.lower())
        if not factory_func:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: {', '.join(providers.keys())}"
            )

        service = factory_func(settings)
        if service is None:
            raise RuntimeError(f"Failed to create {provider} LLM service")

        return service
