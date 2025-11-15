"""Frame processor that runs computer vision analytics on incoming video frames."""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import Awaitable, Callable, Optional

from loguru import logger
from pipecat.frames.frames import Frame, UserImageRawFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from src.services.transcript_service import TranscriptWriter
from src.services.video_analytics_service import (
    EngagementEvent,
    EngagementStateTracker,
    VideoAnalyticsService,
)

EventCallback = Callable[[EngagementEvent], Awaitable[None] | None]


class VideoAnalyticsProcessor(FrameProcessor):
    """Intercept incoming Daily video frames and produce engagement events."""

    def __init__(
        self,
        analytics_service: VideoAnalyticsService,
        state_tracker: EngagementStateTracker,
        *,
        sample_interval_secs: float,
        drop_video_frames: bool = True,
        transcript_writer: Optional[TranscriptWriter] = None,
        event_callback: Optional[EventCallback] = None,
        enable_console_logs: bool = True,
    ) -> None:
        super().__init__(name="VideoAnalyticsProcessor")
        self.analytics_service = analytics_service
        self.state_tracker = state_tracker
        self.sample_interval_secs = sample_interval_secs
        self.drop_video_frames = drop_video_frames
        self.transcript_writer = transcript_writer
        self.event_callback = event_callback
        self.enable_console_logs = enable_console_logs
        self._last_sample_ts: float = 0.0
        self._analysis_lock = asyncio.Lock()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, UserImageRawFrame):
            now = time.time()
            if now - self._last_sample_ts < self.sample_interval_secs:
                if not self.drop_video_frames:
                    await self.push_frame(frame, direction)
                return

            self._last_sample_ts = now
            metrics = await self._run_analytics(frame, now)
            if metrics:
                events = self.state_tracker.update(metrics)
                for event in events:
                    await self._handle_event(event)

            if not self.drop_video_frames:
                await self.push_frame(frame, direction)
            return

        await self.push_frame(frame, direction)

    async def _run_analytics(self, frame: UserImageRawFrame, timestamp: float):
        async with self._analysis_lock:
            return await asyncio.to_thread(
                self.analytics_service.analyze_frame,
                frame,
                timestamp,
            )

    async def _handle_event(self, event: EngagementEvent):
        if self.enable_console_logs:
            logger.info(f"👀 Vision: {event.summary}")

        if self.transcript_writer:
            metadata = {
                "event_type": event.type,
                "attention_score": event.metrics.attention_score,
                "smile_score": event.metrics.smile_score,
            }
            if event.payload:
                metadata.update(event.payload)
            self.transcript_writer.record_event(
                event_type="vision",
                text=event.summary,
                metadata=metadata,
            )

        if self.event_callback:
            result = self.event_callback(event)
            if inspect.isawaitable(result):
                await result
