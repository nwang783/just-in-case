"""
Avatar utilities for streaming video frames to Daily rooms.
Loads PNG assets and exposes processors to animate bot states.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from loguru import logger
from PIL import Image
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    OutputImageRawFrame,
    SpriteFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class AvatarLoadingError(RuntimeError):
    """Raised when avatar frames cannot be loaded."""


@dataclass
class AvatarFrames:
    """Container for avatar frames."""

    quiet_frame: OutputImageRawFrame
    talking_frame: SpriteFrame


class AvatarService:
    """Loads avatar assets from disk."""

    def __init__(self, assets_dir: Path, glob_pattern: str = "*.png"):
        self.assets_dir = Path(assets_dir)
        self.glob_pattern = glob_pattern

    def load_frames(self) -> AvatarFrames:
        """Load avatar frames and build quiet/talking states."""
        frames = self._load_all_frames()
        if not frames:
            raise AvatarLoadingError(
                f"No avatar frames found in {self.assets_dir} matching {self.glob_pattern}"
            )

        quiet_frame = frames[0]
        if len(frames) == 1:
            talking_frames = frames
        else:
            # Mirror frames for smoother looping animation
            talking_frames = frames + frames[-2:0:-1]

        talking_frame = SpriteFrame(images=talking_frames)
        logger.info(
            f"Loaded {len(frames)} avatar frame(s) from {self.assets_dir.resolve()}"
        )
        return AvatarFrames(quiet_frame=quiet_frame, talking_frame=talking_frame)

    def _load_all_frames(self) -> List[OutputImageRawFrame]:
        if not self.assets_dir.exists():
            raise AvatarLoadingError(
                f"Avatar assets directory does not exist: {self.assets_dir}"
            )

        image_paths = sorted(self.assets_dir.glob(self.glob_pattern))
        frames: List[OutputImageRawFrame] = []
        for path in image_paths:
            frames.append(self._load_single_frame(path))
        return frames

    def _load_single_frame(self, path: Path) -> OutputImageRawFrame:
        try:
            with Image.open(path) as img:
                converted = img.convert("RGBA")
                return OutputImageRawFrame(
                    image=converted.tobytes(),
                    size=converted.size,
                    format=converted.mode,
                )
        except Exception as exc:
            raise AvatarLoadingError(f"Failed to load avatar frame {path}") from exc


class AvatarAnimationProcessor(FrameProcessor):
    """Switches between quiet and talking avatar states."""

    def __init__(self, quiet_frame: OutputImageRawFrame, talking_frame: SpriteFrame):
        super().__init__()
        self.quiet_frame = quiet_frame
        self.talking_frame = talking_frame
        self._is_talking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, BotStartedSpeakingFrame):
            if not self._is_talking:
                await self.push_frame(self.talking_frame)
                self._is_talking = True
        elif isinstance(frame, BotStoppedSpeakingFrame):
            await self.push_frame(self.quiet_frame)
            self._is_talking = False

        await self.push_frame(frame, direction)
