"""
Event handlers for conversation flow and custom logic.
"""

import time
from typing import Optional
from loguru import logger
from pipecat.frames.frames import (
    Frame,
    TextFrame,
    LLMTextFrame,
    TranscriptionFrame,
    LLMMessagesFrame,
    LLMFullResponseStartFrame,
    LLMFullResponseEndFrame,
    MetricsFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.metrics.metrics import (
    LLMUsageMetricsData,
    ProcessingMetricsData,
    TTFBMetricsData,
    TTSUsageMetricsData,
)
from src.services.transcript_service import TranscriptWriter


class ConversationHandlers:
    """
    Handlers for conversation events and custom processing.

    This class can be extended to add custom logic for:
    - Tracking conversation state
    - Implementing custom behaviors
    - Logging and analytics
    - Error handling
    """

    def __init__(self):
        """Initialize conversation handlers."""
        self.conversation_started = False
        self.message_count = 0

    async def on_first_participant_joined(self, participant):
        """
        Handle first participant joining the conversation.

        Args:
            participant: Participant information
        """
        logger.info(f"First participant joined: {participant}")
        self.conversation_started = True

    async def on_participant_left(self, participant):
        """
        Handle participant leaving the conversation.

        Args:
            participant: Participant information
        """
        logger.info(f"Participant left: {participant}")

    async def on_user_transcription(self, text: str):
        """
        Handle user speech transcription.

        Args:
            text: Transcribed text from user
        """
        self.message_count += 1
        logger.info(f"User said (message #{self.message_count}): {text}")

        # Add custom logic here, such as:
        # - Intent detection
        # - Keyword tracking
        # - Analytics
        # - Custom responses to specific phrases

    async def on_bot_response(self, text: str):
        """
        Handle bot text response before TTS.

        Args:
            text: Bot's text response
        """
        logger.info(f"Bot responding: {text}")

        # Add custom logic here, such as:
        # - Response filtering
        # - Custom formatting
        # - Logging for analytics

    async def on_error(self, error: Exception):
        """
        Handle errors in the conversation.

        Args:
            error: Exception that occurred
        """
        logger.error(f"Conversation error: {error}", exc_info=True)

        # Add custom error handling here, such as:
        # - Error recovery
        # - Fallback responses
        # - Notifications

    async def on_conversation_end(self):
        """Handle conversation ending."""
        logger.info("Conversation ended")
        logger.info(f"Total messages exchanged: {self.message_count}")

        # Add cleanup logic here, such as:
        # - Saving conversation history
        # - Analytics recording
        # - Resource cleanup


class TranscriptLogger(FrameProcessor):
    """
    Frame processor that logs transcripts and LLM context in development mode.

    This helps debug what the user is saying and what context is being sent to the LLM.
    Tracks latency at each stage of the pipeline.
    """

    def __init__(
        self,
        transcript_writer: Optional[TranscriptWriter] = None,
        enable_console_logs: bool = True,
        **kwargs,
    ):
        """Initialize the transcript logger."""
        super().__init__(name="TranscriptLogger", **kwargs)
        self.user_message_count = 0
        self.transcript_writer = transcript_writer
        self.enable_console_logs = enable_console_logs
        self.bot_message_count = 0

        # Track current response being built
        self.current_bot_response = ""
        self.response_start_time = None

        # Track timestamps for latency measurement
        self.user_speech_end_time = None
        self.llm_start_time = None
        self.llm_end_time = None
        self.tts_start_time = None
        self.first_audio_time = None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """
        Process frames and log transcripts and LLM messages.

        Args:
            frame: Frame to process
            direction: Direction of frame flow
        """
        # Call parent to handle system frames (StartFrame, etc.)
        await super().process_frame(frame, direction)

        # Log user transcriptions (final transcription from STT)
        if isinstance(frame, TranscriptionFrame):
            self.user_message_count += 1
            self.user_speech_end_time = time.time()
            if self.enable_console_logs:
                logger.info(f"\n{'='*80}")
                logger.info(f"📝 [User #{self.user_message_count}] {frame.text}")
                logger.info(f"{'='*80}\n")
            if self.transcript_writer:
                self.transcript_writer.record_message("user", frame.text)

        # Track when user aggregator sends context to LLM (going downstream)
        if isinstance(frame, LLMMessagesFrame) and direction == FrameDirection.DOWNSTREAM:
            self.llm_start_time = time.time()
            if self.user_speech_end_time:
                latency = (self.llm_start_time - self.user_speech_end_time) * 1000
                if self.enable_console_logs:
                    logger.info(f"⏱️  STT → LLM latency: {latency:.2f}ms")

        # Only log STT metrics from this logger (filter out the initial 0.00ms ones)
        if isinstance(frame, MetricsFrame) and self.enable_console_logs:
            for metric_data in frame.data:
                processor_name = metric_data.processor if hasattr(metric_data, 'processor') else "Unknown"

                # Only log STT metrics here, skip if value is 0
                if "STT" in processor_name or "Deepgram" in processor_name:
                    if isinstance(metric_data, TTFBMetricsData) and metric_data.value > 0:
                        ttfb_ms = metric_data.value * 1000
                        logger.info(f"⏱️  {processor_name} TTFB: {ttfb_ms:.2f}ms")
                    elif isinstance(metric_data, ProcessingMetricsData) and metric_data.value > 0:
                        processing_ms = metric_data.value * 1000
                        logger.info(f"⏱️  {processor_name} Processing Time: {processing_ms:.2f}ms")

        # Pass frame through unchanged
        await self.push_frame(frame, direction)


class BotResponseLogger(FrameProcessor):
    """
    Frame processor that captures bot responses and LLM/TTS metrics.

    This should be placed AFTER the LLM in the pipeline to see:
    - LLM response frames
    - LLM metrics (TTFB, processing time, token usage)
    - TTS metrics
    """

    def __init__(
        self,
        transcript_writer: Optional[TranscriptWriter] = None,
        enable_console_logs: bool = True,
        **kwargs,
    ):
        """Initialize the bot response logger."""
        super().__init__(name="BotResponseLogger", **kwargs)
        self.bot_message_count = 0
        self.current_bot_response = ""
        self.transcript_writer = transcript_writer
        self.enable_console_logs = enable_console_logs

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """
        Process frames to capture bot responses and metrics.

        Args:
            frame: Frame to process
            direction: Direction of frame flow
        """
        # Call parent to handle system frames
        await super().process_frame(frame, direction)

        # Track LLM response start
        if isinstance(frame, LLMFullResponseStartFrame):
            self.current_bot_response = ""

        # Collect bot response text as it streams
        if isinstance(frame, LLMTextFrame):
            if hasattr(frame, 'text') and frame.text:
                self.current_bot_response += frame.text

        # Log complete bot response when LLM finishes
        if isinstance(frame, LLMFullResponseEndFrame):
            self.bot_message_count += 1
            if self.enable_console_logs:
                logger.info(f"\n{'='*80}")
                logger.info(f"🤖 [Bot #{self.bot_message_count}] {self.current_bot_response}")
                logger.info(f"{'='*80}\n")
            if self.transcript_writer and self.current_bot_response:
                self.transcript_writer.record_message("assistant", self.current_bot_response)

        # Handle metrics frames for LLM and TTS
        if isinstance(frame, MetricsFrame) and self.enable_console_logs:
            for metric_data in frame.data:
                processor_name = metric_data.processor if hasattr(metric_data, 'processor') else "Unknown"

                if isinstance(metric_data, TTFBMetricsData):
                    ttfb_ms = metric_data.value * 1000
                    logger.info(f"⏱️  {processor_name} TTFB: {ttfb_ms:.2f}ms")

                elif isinstance(metric_data, ProcessingMetricsData):
                    processing_ms = metric_data.value * 1000
                    logger.info(f"⏱️  {processor_name} Processing Time: {processing_ms:.2f}ms")

                elif isinstance(metric_data, LLMUsageMetricsData):
                    tokens = metric_data.value
                    logger.info(f"📊 {processor_name} Usage - Prompt: {tokens.prompt_tokens}, Completion: {tokens.completion_tokens} tokens")

                elif isinstance(metric_data, TTSUsageMetricsData):
                    logger.info(f"📊 {processor_name} Usage - {metric_data.value} characters")

        # Pass frame through unchanged
        await self.push_frame(frame, direction)


class CustomFrameProcessor:
    """
    Custom frame processor for advanced pipeline manipulation.

    This can be used to intercept and modify frames in the pipeline.
    """

    async def process_frame(self, frame: Frame) -> Optional[Frame]:
        """
        Process a frame in the pipeline.

        Args:
            frame: Frame to process

        Returns:
            Modified frame or None to filter it out
        """
        # Example: Log all text frames
        if isinstance(frame, TextFrame):
            logger.debug(f"Text frame: {frame.text}")

        # Example: Log all transcriptions
        if isinstance(frame, TranscriptionFrame):
            logger.debug(f"Transcription: {frame.text}")

        # Return the frame unchanged (or modify it)
        return frame
