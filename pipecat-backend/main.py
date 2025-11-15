#!/usr/bin/env python3
"""
Main entry point for the Case Interview Coach voice agent.

Usage:
    python main.py

Environment variables are loaded from .env file.
See .env.example for required configuration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import settings
from src.utils.logger import setup_logger
from src.bot.voice_agent import VoiceAgent


async def main():
    """Main application entry point."""
    # Setup logging
    setup_logger(
        log_level=settings.log_level,
        environment=settings.environment
    )

    from loguru import logger
    logger.info("=" * 60)
    logger.info("Starting Pipecat Voice Agent")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Bot Name: {settings.bot_name}")
    logger.info(f"Daily Room: {settings.daily_room_url}")
    logger.info(f"LLM Provider: openai")
    logger.info(f"TTS Provider: cartesia")
    logger.info(f"STT Provider: deepgram")
    logger.info("=" * 60)

    # Validate configuration
    if not settings.daily_room_url:
        logger.error("DAILY_ROOM_URL not configured!")
        logger.error("Please set DAILY_ROOM_URL in your .env file")
        logger.error("Example: DAILY_ROOM_URL=https://your-domain.daily.co/your-room")
        sys.exit(1)

    # Create and run voice agent
    try:
        agent = VoiceAgent(
            settings=settings,
            llm_provider="openai",      # Can be changed to "anthropic"
            tts_provider="cartesia",     # Using Cartesia for low-latency TTS
            stt_provider="deepgram",     # Default STT provider
        )

        # Run the agent (this will block until stopped)
        await agent.run()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Voice agent stopped")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
