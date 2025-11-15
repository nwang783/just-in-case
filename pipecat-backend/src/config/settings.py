"""
Configuration management for the Pipecat voice agent.
Uses Pydantic Settings for type-safe environment variable handling.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger

# Resolve project root so .env is loaded regardless of working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Daily.co Configuration (WebRTC Transport)
    daily_api_key: str = Field(..., description="Daily.co API key")
    daily_room_url: Optional[str] = Field(None, description="Daily.co room URL")
    daily_auto_create_room: bool = Field(
        default=False,
        description="Automatically create a Daily room for each run"
    )
    daily_room_prefix: str = Field(
        default="case-coach",
        description="Prefix for auto-created Daily rooms"
    )
    daily_room_exp_minutes: int = Field(
        default=120,
        ge=0,
        description="Minutes until auto-created rooms expire (0 disables expiration)"
    )
    avatar_enabled: bool = Field(
        default=False,
        description="Enable streaming an avatar image sequence to the Daily room"
    )
    avatar_assets_dir: str = Field(
        default="assets",
        description="Relative or absolute path to avatar image frames"
    )
    avatar_frame_glob: str = Field(
        default="*.png",
        description="Glob pattern for avatar frames within the assets directory"
    )
    avatar_frame_repeat: int = Field(
        default=1,
        ge=1,
        description="Repeat each avatar frame N times to slow down animation"
    )

    # OpenAI Configuration (LLM and TTS)
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use")

    # Deepgram Configuration (STT)
    deepgram_api_key: str = Field(..., description="Deepgram API key for STT")

    # Alternative LLM: Anthropic Claude (optional)
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model to use"
    )

    # Alternative TTS: ElevenLabs (optional)
    elevenlabs_api_key: Optional[str] = Field(None, description="ElevenLabs API key")
    elevenlabs_voice_id: Optional[str] = Field(None, description="ElevenLabs voice ID")

    # Alternative TTS: Cartesia (optional)
    cartesia_api_key: Optional[str] = Field(None, description="Cartesia API key")
    cartesia_voice_id: str = Field(
        default="79a125e8-cd45-4c13-8a67-188112f4dd22",
        description="Cartesia voice ID (default: British Lady)"
    )
    cartesia_model: str = Field(
        default="sonic-english",
        description="Cartesia model to use"
    )

    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Bot Configuration
    bot_name: str = Field(default="Case Interview Coach", description="Bot display name")
    bot_greeting: str = Field(
        default="Hi! I'm ready to practice a case interview with you. Should we get started?",
        description="Initial bot greeting"
    )
    system_prompt_file: str = Field(
        default="case_interviewer.txt",
        description="System prompt file name (relative to src/system_prompts/)"
    )
    transcripts_enabled: bool = Field(
        default=True,
        description="Persist conversation transcripts to disk"
    )
    transcripts_output_dir: str = Field(
        default="output",
        description="Directory for archived transcripts (relative to project root or absolute path)"
    )
    transcript_analysis_enabled: bool = Field(
        default=True,
        description="Analyze transcripts with OpenAI when a session ends"
    )
    transcript_analysis_model: str = Field(
        default="gpt-5-nano",
        description="Model used for transcript analysis"
    )
    transcript_analysis_output_dir: str = Field(
        default="output/analysis",
        description="Directory to store structured transcript analysis"
    )

    # VAD (Voice Activity Detection) Configuration
    vad_enabled: bool = Field(default=True, description="Enable VAD for speech detection")
    vad_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="VAD confidence threshold (0.0-1.0)"
    )
    vad_start_secs: float = Field(
        default=0.2,
        ge=0.0,
        description="Seconds before confirming speech start"
    )
    vad_stop_secs: float = Field(
        default=0.8,
        ge=0.0,
        description="Seconds of silence before confirming speech stop"
    )
    vad_min_volume: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum volume threshold (0.0-1.0)"
    )

    # Turn Detection Configuration
    turn_detection_enabled: bool = Field(
        default=False,
        description="Enable smart turn detection for better conversation flow"
    )

    # Vision Analytics (Video Engagement)
    vision_analytics_enabled: bool = Field(
        default=False,
        description="Enable camera-based engagement and emotion analytics"
    )
    vision_target_fps: float = Field(
        default=6.0,
        ge=1.0,
        le=30.0,
        description="Maximum number of frames per second to analyze from the user's camera"
    )
    vision_max_frame_width: int = Field(
        default=640,
        ge=64,
        description="Resize incoming frames to this width before running CV models"
    )
    vision_eye_ar_threshold: float = Field(
        default=0.18,
        ge=0.05,
        le=0.5,
        description="Eye aspect ratio threshold used to detect closed eyes"
    )
    vision_look_away_threshold: float = Field(
        default=0.12,
        ge=0.02,
        le=0.5,
        description="Normalized horizontal offset threshold to mark a user as looking away"
    )
    vision_smile_threshold: float = Field(
        default=0.25,
        ge=0.05,
        le=1.0,
        description="Smile width ratio threshold (relative to face width)"
    )
    vision_min_event_gap_secs: float = Field(
        default=2.5,
        ge=0.5,
        description="Minimum seconds between emitting repeated engagement events"
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    @property
    def transcripts_dir(self) -> Path:
        """Resolved absolute path to the transcripts output directory."""
        output_path = Path(self.transcripts_output_dir)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
        return output_path

    @property
    def transcript_analysis_dir(self) -> Path:
        """Resolved absolute path to the transcript analysis output directory."""
        output_path = Path(self.transcript_analysis_output_dir)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
        return output_path

    def load_system_prompt(self) -> str:
        """Load the system prompt from the configured file.

        Returns:
            str: The system prompt content

        Raises:
            FileNotFoundError: If the system prompt file doesn't exist
        """
        # Get the path to the system_prompts directory
        # Assuming this settings.py is in src/config/
        project_root = Path(__file__).parent.parent
        prompts_dir = project_root / "system_prompts"
        prompt_file = prompts_dir / self.system_prompt_file

        if not prompt_file.exists():
            logger.error(f"System prompt file not found: {prompt_file}")
            raise FileNotFoundError(f"System prompt file not found: {prompt_file}")

        logger.info(f"Loading system prompt from: {prompt_file}")

        with open(prompt_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        logger.debug(f"Loaded system prompt ({len(content)} characters)")
        return content

    def avatar_assets_path(self) -> Path:
        """Return the absolute path to the avatar assets directory."""
        assets_path = Path(self.avatar_assets_dir)
        if assets_path.is_absolute():
            return assets_path
        # Allow prefixes like "pipecat-backend/assets" without duplicating the root
        if assets_path.parts and assets_path.parts[0] == PROJECT_ROOT.name:
            return PROJECT_ROOT.parent / assets_path
        return PROJECT_ROOT / assets_path


# Global settings instance
settings = Settings()
