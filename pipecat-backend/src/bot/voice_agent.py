"""
Voice Agent Pipeline Orchestration.
Constructs and manages the Pipecat pipeline (STT → LLM → TTS).
"""

from typing import Optional
from loguru import logger

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.pipeline.runner import PipelineRunner
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.frames.frames import EndFrame

from src.config.settings import Settings
from src.config.vad_config import VADConfig
from src.services.llm_service import LLMServiceFactory
from src.services.tts_service import TTSServiceFactory
from src.services.stt_service import STTServiceFactory
from src.transport.daily_transport import DailyTransportFactory
from src.services.daily_room_service import DailyRoomService, DailyRoomCreationError, DailyRoom


class VoiceAgent:
    """
    Voice agent that orchestrates the conversation pipeline.

    Architecture:
    Transport Input → STT → LLM Context → LLM → TTS → Transport Output
    """

    def __init__(
        self,
        settings: Settings,
        llm_provider: str = "openai",
        tts_provider: str = "cartesia",
        stt_provider: str = "deepgram",
        room_url: Optional[str] = None,
    ):
        """
        Initialize the voice agent.

        Args:
            settings: Application settings
            llm_provider: LLM provider to use ("openai" or "anthropic")
            tts_provider: TTS provider to use ("openai" or "elevenlabs")
            stt_provider: STT provider to use ("deepgram" or "azure")
            room_url: Optional Daily room URL (overrides settings)
        """
        self.settings = settings
        self.llm_provider = llm_provider
        self.tts_provider = tts_provider
        self.stt_provider = stt_provider
        self.room_url = room_url
        self.created_room: Optional[DailyRoom] = None

        logger.info(f"Initializing Voice Agent with providers:")
        logger.info(f"  LLM: {llm_provider}")
        logger.info(f"  TTS: {tts_provider}")
        logger.info(f"  STT: {stt_provider}")

        # Initialize services
        self.transport = None
        self.stt = None
        self.llm = None
        self.tts = None
        self.context = None
        self.pipeline = None
        self.task = None

    def _resolve_room_url(self) -> str:
        """
        Determine which Daily room URL to use for this run.

        Preference order:
        1. Explicit room_url passed into the constructor
        2. Auto-create a room if enabled in settings
        3. Fallback to the static DAILY_ROOM_URL
        """
        if self.room_url:
            logger.info(f"Using provided Daily room URL: {self.room_url}")
            return self.room_url

        if self.settings.daily_auto_create_room:
            logger.info("Auto room creation enabled - creating new Daily room")
            room_service = DailyRoomService(self.settings)
            try:
                self.created_room = room_service.create_room()
            except DailyRoomCreationError as exc:
                raise RuntimeError(
                    "Failed to auto-create Daily room. "
                    "Check your Daily API key and permissions."
                ) from exc

            self.room_url = self.created_room.url
            logger.info(f"Daily room created: {self.room_url}")
            if self.created_room.expires_at:
                logger.info(
                    f"Room expires at {self.created_room.pretty_expiration()}"
                )
            logger.info("Share this link with participants to join the session.")
            return self.room_url

        if self.settings.daily_room_url:
            self.room_url = self.settings.daily_room_url
            logger.info(f"Using configured Daily room URL: {self.room_url}")
            return self.room_url

        raise ValueError(
            "No Daily room available. Provide DAILY_ROOM_URL or enable auto creation."
        )

    def _create_services(self):
        """Create all required services."""
        logger.info("Creating services...")
        resolved_room_url = self._resolve_room_url()

        # Create VAD analyzer if enabled
        vad_analyzer = None
        turn_analyzer = None

        if self.settings.vad_enabled:
            logger.info("VAD is enabled - creating VAD analyzer")

            # Adjust stop_secs if turn detection is enabled
            stop_secs = self.settings.vad_stop_secs
            if self.settings.turn_detection_enabled:
                logger.info("Turn detection enabled - setting VAD stop_secs to 0.2")
                stop_secs = 0.2

            vad_analyzer = VADConfig.create_vad_analyzer(
                confidence=self.settings.vad_confidence,
                start_secs=self.settings.vad_start_secs,
                stop_secs=stop_secs,
                min_volume=self.settings.vad_min_volume,
            )

            # Create turn analyzer if enabled
            if self.settings.turn_detection_enabled:
                logger.info("Creating turn analyzer")
                turn_analyzer = VADConfig.create_smart_turn_analyzer()
                if turn_analyzer is None:
                    logger.warning(
                        "Turn detection requested but not available. "
                        "Continuing with VAD only."
                    )
        else:
            logger.info("VAD is disabled in settings")

        # Create transport
        self.transport = DailyTransportFactory.create_transport(
            settings=self.settings,
            room_url=resolved_room_url,
            audio_out_enabled=True,
            audio_in_enabled=True,
            vad_analyzer=vad_analyzer,
            turn_analyzer=turn_analyzer,
        )

        # Create STT service
        self.stt = STTServiceFactory.create_stt(
            settings=self.settings,
            provider=self.stt_provider,
        )

        # Create LLM service
        self.llm = LLMServiceFactory.create_llm(
            settings=self.settings,
            provider=self.llm_provider,
        )

        # Create TTS service
        self.tts = TTSServiceFactory.create_tts(
            settings=self.settings,
            provider=self.tts_provider,
        )

        logger.info("All services created successfully")

    def _create_llm_context(self) -> OpenAILLMContext:
        """
        Create the LLM context with system prompt and initial messages.

        Returns:
            Configured OpenAI LLM context
        """
        # Load the system prompt from file
        logger.info("Loading system prompt from file")
        system_prompt = self.settings.load_system_prompt()

        # Create context with system message
        context = OpenAILLMContext(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                }
            ],
        )

        logger.info("LLM context created with system prompt")
        return context

    def _create_pipeline(self):
        """Create the Pipecat processing pipeline."""
        logger.info("Creating pipeline...")

        # Create LLM context
        self.context = self._create_llm_context()

        # Create context aggregators for managing conversation flow
        from pipecat.processors.aggregators.llm_response import (
            LLMUserContextAggregator,
            LLMAssistantContextAggregator,
        )

        user_aggregator = LLMUserContextAggregator(self.context)
        assistant_aggregator = LLMAssistantContextAggregator(self.context)

        # Build the pipeline with comprehensive logging
        pipeline_processors = [
            self.transport.input(),           # Audio input from Daily
            self.stt,                          # Speech-to-Text
        ]

        # Add transcript logger AFTER STT to capture user transcripts and STT metrics
        if self.settings.is_development:
            from src.bot.handlers import TranscriptLogger
            transcript_logger = TranscriptLogger()
            pipeline_processors.append(transcript_logger)

        # Continue with user aggregator and LLM
        pipeline_processors.extend([
            user_aggregator,                   # Aggregate user messages
            self.llm,                          # Language Model processing
        ])

        # Add bot response logger AFTER LLM to capture bot responses and LLM/TTS metrics
        if self.settings.is_development:
            from src.bot.handlers import BotResponseLogger
            bot_logger = BotResponseLogger()
            pipeline_processors.append(bot_logger)

        # Continue with rest of pipeline
        pipeline_processors.extend([
            self.tts,                          # Text-to-Speech
            self.transport.output(),           # Audio output to Daily
            assistant_aggregator,              # Aggregate assistant responses
        ])

        # Build the pipeline
        self.pipeline = Pipeline(pipeline_processors)

        logger.info("Pipeline created successfully")

    def _create_task(self) -> PipelineTask:
        """
        Create the pipeline task with configuration.

        Returns:
            Configured PipelineTask
        """
        logger.info("Creating pipeline task...")

        # Configure pipeline parameters
        params = PipelineParams(
            enable_metrics=True,           # Enable performance metrics
            enable_usage_metrics=True,     # Enable usage tracking
            allow_interruptions=True,      # Enable natural interruptions (default: True)
        )

        # Create and return task
        self.task = PipelineTask(
            self.pipeline,
            params=params,
        )

        # Optional: Send initial greeting
        if self.settings.bot_greeting:
            logger.info(f"Setting bot greeting: {self.settings.bot_greeting}")
            # The greeting will be sent when the conversation starts

        logger.info("Pipeline task created successfully")
        return self.task

    async def run(self):
        """
        Run the voice agent.

        This is the main entry point that starts the bot and keeps it running.
        """
        try:
            logger.info("Starting Voice Agent...")

            # Create all services
            self._create_services()

            # Create the pipeline
            self._create_pipeline()

            # Create the task
            task = self._create_task()

            # Optional: Send greeting message
            if self.settings.bot_greeting:
                initial_context = OpenAILLMContextFrame(self.context)
                await task.queue_frame(initial_context)
                # Note: To actually speak the greeting, you'd need to queue TTS frames

            # Create and run the pipeline runner
            runner = PipelineRunner()

            logger.info("Voice Agent is now running. Press Ctrl+C to stop.")
            await runner.run(task)

        except KeyboardInterrupt:
            logger.info("Voice Agent stopped by user")
        except Exception as e:
            logger.error(f"Error running voice agent: {e}", exc_info=True)
            raise
        finally:
            # Cleanup
            logger.info("Cleaning up...")
            if self.task:
                await self.task.queue_frame(EndFrame())

    async def stop(self):
        """Stop the voice agent gracefully."""
        logger.info("Stopping Voice Agent...")
        if self.task:
            await self.task.queue_frame(EndFrame())
