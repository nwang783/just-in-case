"""
Computer vision utilities for engagement and emotion tracking using OpenCV.

The processor leverages Haar cascades (faces/eyes/smiles) to derive attention
and mood signals from the user's camera feed without requiring MediaPipe.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Literal, Optional

import numpy as np
from loguru import logger
from pipecat.frames.frames import UserImageRawFrame

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None  # type: ignore[assignment]


@dataclass
class VideoAnalyticsConfig:
    """Configuration for the video analytics service."""

    target_fps: float
    max_frame_width: int
    eye_aspect_ratio_threshold: float
    look_away_threshold: float
    smile_threshold: float


@dataclass
class EngagementMetrics:
    """Continuous engagement metrics computed per sampled frame."""

    timestamp: float
    user_id: str
    face_detected: bool
    attention_score: float
    looking_away: bool
    eyes_closed: bool
    eye_aspect_ratio: float
    smile_score: float
    is_smiling: bool
    frame_size: tuple[int, int]


@dataclass
class EngagementEvent:
    """Discrete engagement events emitted when state changes."""

    type: Literal["attention", "smile"]
    summary: str
    metrics: EngagementMetrics
    payload: Optional[Dict[str, Any]] = None


class VideoAnalyticsService:
    """
    Run OpenCV cascade detectors on user camera frames to estimate engagement.

    Haar cascades are fast on CPU and provide coarse measurements of gaze,
    eye openness, and smiles without requiring GPU acceleration.
    """

    def __init__(self, config: VideoAnalyticsConfig) -> None:
        if cv2 is None:
            raise RuntimeError("Video analytics requires opencv-python to be installed.")

        self.config = config
        self._lock = Lock()
        haar_dir = Path(cv2.data.haarcascades)
        self.face_cascade = cv2.CascadeClassifier(str(haar_dir / "haarcascade_frontalface_default.xml"))
        self.eye_cascade = cv2.CascadeClassifier(str(haar_dir / "haarcascade_eye.xml"))
        self.smile_cascade = cv2.CascadeClassifier(str(haar_dir / "haarcascade_smile.xml"))
        if self.face_cascade.empty() or self.eye_cascade.empty() or self.smile_cascade.empty():
            raise RuntimeError("Failed to load OpenCV Haar cascade files for video analytics.")

        logger.info(
            "Initialized VideoAnalyticsService "
            f"(target_fps={config.target_fps}, max_width={config.max_frame_width})"
        )

    def close(self) -> None:
        """Nothing to clean up for the OpenCV-based analyzer."""

    def analyze_frame(self, frame: UserImageRawFrame, timestamp: float) -> EngagementMetrics:
        """
        Analyze a single video frame and produce engagement metrics.

        Args:
            frame: Raw image frame from Daily transport.
            timestamp: Timestamp associated with the frame.
        """
        with self._lock:
            np_frame = self._prepare_image(frame)

        gray = cv2.cvtColor(np_frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        metrics = EngagementMetrics(
            timestamp=timestamp,
            user_id=frame.user_id or "unknown",
            face_detected=False,
            attention_score=0.0,
            looking_away=False,
            eyes_closed=True,
            eye_aspect_ratio=0.0,
            smile_score=0.0,
            is_smiling=False,
            frame_size=(np_frame.shape[1], np_frame.shape[0]),
        )

        if len(faces) == 0:
            return metrics

        # Use the largest detected face as the primary signal.
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        face_roi = gray[y : y + h, x : x + w]

        # Estimate gaze based on face position within the frame.
        center_x = (x + w / 2) / gray.shape[1]
        center_offset = abs(center_x - 0.5)
        looking_away = center_offset > self.config.look_away_threshold
        attention_score = max(
            0.0,
            1.0 - min(1.0, center_offset / max(self.config.look_away_threshold, 1e-3)),
        )

        # Detect eyes to approximate eye-aspect ratio (height/width of box).
        eyes = self.eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=5)
        eye_ratio = 0.0
        if len(eyes) > 0:
            eye_w = max(1, eyes[0][2])
            eye_h = max(1, eyes[0][3])
            eye_ratio = eye_h / eye_w

        # Smile detection relies on relative mouth width within the face box.
        smiles = self.smile_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.3,
            minNeighbors=20,
        )
        smile_ratio = 0.0
        if len(smiles) > 0:
            smile_ratio = max(smile_w / w for (_, _, smile_w, _) in smiles)

        metrics.face_detected = True
        metrics.eye_aspect_ratio = eye_ratio
        metrics.smile_score = smile_ratio
        metrics.attention_score = attention_score
        metrics.eyes_closed = eye_ratio < self.config.eye_aspect_ratio_threshold
        metrics.looking_away = looking_away
        metrics.is_smiling = smile_ratio > self.config.smile_threshold

        return metrics

    def _prepare_image(self, frame: UserImageRawFrame) -> np.ndarray:
        """Decode and downscale the frame to the configured width."""
        width, height = frame.size
        array = np.frombuffer(frame.image, dtype=np.uint8).reshape((height, width, 3))

        if frame.format.upper() == "BGR":
            array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)

        if width > self.config.max_frame_width:
            ratio = self.config.max_frame_width / width
            new_height = max(64, int(height * ratio))
            array = cv2.resize(array, (self.config.max_frame_width, new_height))

        array.setflags(write=False)
        return array


class EngagementStateTracker:
    """Track engagement states and emit discrete events on transitions."""

    def __init__(self, min_event_gap_secs: float = 2.5) -> None:
        self.min_event_gap_secs = min_event_gap_secs
        self._attention_state: Literal["unknown", "attentive", "distracted"] = "unknown"
        self._smiling: bool = False
        self._last_attention_event: float = 0.0
        self._last_smile_event: float = 0.0

    def update(self, metrics: EngagementMetrics) -> List[EngagementEvent]:
        """Update state from new metrics and return any generated events."""
        events: List[EngagementEvent] = []
        now = metrics.timestamp

        next_attention_state, reason = self._attention_state_for_metrics(metrics)
        if next_attention_state != self._attention_state:
            should_emit = (now - self._last_attention_event) >= self.min_event_gap_secs
            self._attention_state = next_attention_state
            if should_emit:
                summary = self._compose_attention_summary(next_attention_state, reason, metrics)
                events.append(
                    EngagementEvent(
                        type="attention",
                        summary=summary,
                        metrics=metrics,
                        payload={"reason": reason} if reason else None,
                    )
                )
                self._last_attention_event = now

        smiling = metrics.is_smiling
        if smiling != self._smiling:
            should_emit = (now - self._last_smile_event) >= self.min_event_gap_secs
            self._smiling = smiling
            if should_emit:
                summary = (
                    f"User started smiling (score {metrics.smile_score:.2f})"
                    if smiling
                    else "User stopped smiling."
                )
                events.append(
                    EngagementEvent(
                        type="smile",
                        summary=summary,
                        metrics=metrics,
                        payload={
                            "smile_score": metrics.smile_score,
                            "smiling": smiling,
                        },
                    )
                )
                self._last_smile_event = now

        return events

    def _attention_state_for_metrics(
        self, metrics: EngagementMetrics
    ) -> tuple[Literal["attentive", "distracted"], Optional[str]]:
        if not metrics.face_detected:
            return "distracted", "lost face tracking"
        if metrics.eyes_closed:
            return "distracted", "eyes closed"
        if metrics.looking_away:
            return "distracted", "looking away from the screen"
        return "attentive", None

    @staticmethod
    def _compose_attention_summary(
        state: Literal["attentive", "distracted"],
        reason: Optional[str],
        metrics: EngagementMetrics,
    ) -> str:
        if state == "attentive":
            return (
                "User re-engaged with the interview "
                f"(attention {metrics.attention_score:.2f})."
            )
        detail = f" ({reason})" if reason else ""
        return (
            "User disengaged or lost attention"
            f"{detail}."
        )
