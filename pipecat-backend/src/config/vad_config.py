"""
VAD (Voice Activity Detection) configuration for Pipecat.
Provides Silero VAD analyzer with configurable parameters for speech detection.
"""

from typing import Optional
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams


class VADConfig:
    """Factory for creating VAD analyzer instances with configurable parameters."""

    @staticmethod
    def create_vad_analyzer(
        confidence: float = 0.7,
        start_secs: float = 0.2,
        stop_secs: float = 0.8,
        min_volume: float = 0.6,
    ) -> SileroVADAnalyzer:
        """
        Create a Silero VAD analyzer with specified parameters.

        Args:
            confidence: Minimum confidence for voice detection (0.0-1.0)
                       Default: 0.7 - works well for most use cases
            start_secs: Time to wait before confirming speech start
                       Lower = more responsive, may trigger on brief sounds
                       Higher = less sensitive, may miss quick utterances
                       Default: 0.2 seconds
            stop_secs: Time of silence before confirming speech has stopped
                      Critical for turn-taking behavior
                      Default: 0.8 seconds (0.2 if using turn detection)
            min_volume: Minimum volume threshold (0.0-1.0)
                       Default: 0.6 - works well for most use cases

        Returns:
            Configured SileroVADAnalyzer instance

        Note:
            - Silero VAD runs locally on CPU with minimal overhead
            - Processes 30+ms audio chunks in less than 1ms
            - confidence and min_volume should only be changed after extensive testing
        """
        logger.info("Creating Silero VAD analyzer with parameters:")
        logger.info(f"  confidence: {confidence}")
        logger.info(f"  start_secs: {start_secs}")
        logger.info(f"  stop_secs: {stop_secs}")
        logger.info(f"  min_volume: {min_volume}")

        vad_params = VADParams(
            confidence=confidence,
            start_secs=start_secs,
            stop_secs=stop_secs,
            min_volume=min_volume,
        )

        return SileroVADAnalyzer(params=vad_params)

    @staticmethod
    def create_smart_turn_analyzer() -> Optional[object]:
        """
        Create a Smart Turn analyzer for advanced turn detection.

        Smart Turn uses a native audio model to detect conversation turns
        based on grammar, tone, pace, and semantic cues.

        Returns:
            LocalSmartTurnAnalyzerV3 instance or None if not available

        Note:
            - Requires VAD to be configured with stop_secs=0.2
            - Supports 23 languages
            - Runs on CPU (no GPU required)
            - When used, VAD behavior adjusts based on turn completion:
              * Complete turn: Normal VAD stop behavior
              * Incomplete turn: Extended waiting time (default: 3.0s)
        """
        try:
            from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import (
                LocalSmartTurnAnalyzerV3,
            )

            logger.info("Creating Smart Turn analyzer (v3)")
            return LocalSmartTurnAnalyzerV3()
        except ImportError:
            logger.warning(
                "Smart Turn analyzer not available. "
                "Install with: pip install pipecat-ai[smart-turn]"
            )
            return None
