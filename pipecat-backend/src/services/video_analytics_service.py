"""
Computer vision utilities for engagement and emotion tracking.

This module uses MediaPipe Face Mesh to derive lightweight metrics such as
eye openness, gaze direction, and smile intensity from incoming video frames.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, List, Literal, Optional

import numpy as np
from loguru import logger
from pipecat.frames.frames import UserImageRawFrame

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None  # type: ignore[assignment]

try:
    import mediapipe as mp  # type: ignore
except ImportError:
    mp = None  # type: ignore[assignment]


LEFT_EYE_LANDMARKS = (33, 133, 159, 145)
RIGHT_EYE_LANDMARKS = (263, 362, 386, 374)
MOUTH_LANDMARKS = (61, 291, 13, 14)
NOSE_TIP_LANDMARK = 1


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
    Run MediaPipe Face Mesh on user camera frames to estimate engagement.

    The heavy lifting happens inside MediaPipe and OpenCV; locking ensures that
    in-flight analyses do not step on each other even if the processor schedules
    them from multiple threads.
    """

    def __init__(self, config: VideoAnalyticsConfig) -> None:
        if cv2 is None or mp is None:
            missing = [
                name for name, module in (("opencv-python", cv2), ("mediapipe", mp)) if module is None
            ]
            raise RuntimeError(
                "Video analytics requires the following packages: "
                + ", ".join(missing)
            )

        self.config = config
        self._lock = Lock()
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(  # type: ignore[attr-defined]
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )

        logger.info(
            "Initialized VideoAnalyticsService "
            f"(target_fps={config.target_fps}, max_width={config.max_frame_width})"
        )

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._face_mesh:
            self._face_mesh.close()

    def analyze_frame(self, frame: UserImageRawFrame, timestamp: float) -> EngagementMetrics:
        """
        Analyze a single video frame and produce engagement metrics.

        Args:
            frame: Raw image frame from Daily transport.
            timestamp: Timestamp associated with the frame.
        """
        with self._lock:
            np_frame = self._prepare_image(frame)
            results = self._face_mesh.process(np_frame)

        metrics = EngagementMetrics(
            timestamp=timestamp,
            user_id=frame.user_id or "unknown",
            face_detected=False,
            attention_score=0.0,
            looking_away=False,
            eyes_closed=False,
            eye_aspect_ratio=0.0,
            smile_score=0.0,
            is_smiling=False,
            frame_size=(np_frame.shape[1], np_frame.shape[0]),
        )

        if not results.multi_face_landmarks:
            return metrics

        landmarks = results.multi_face_landmarks[0].landmark

        eye_ratio = self._eye_aspect_ratio(landmarks)
        mouth_ratio = self._mouth_ratio(landmarks)
        looking_away, attention_score = self._attention_estimate(landmarks)

        metrics.face_detected = True
        metrics.eye_aspect_ratio = eye_ratio
        metrics.smile_score = mouth_ratio
        metrics.attention_score = attention_score
        metrics.eyes_closed = eye_ratio < self.config.eye_aspect_ratio_threshold
        metrics.looking_away = looking_away
        metrics.is_smiling = mouth_ratio > self.config.smile_threshold

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

        # MediaPipe expects the array to be read-only for performance.
        array.setflags(write=False)
        return array

    def _eye_aspect_ratio(self, landmarks) -> float:
        left = self._compute_ear(landmarks, LEFT_EYE_LANDMARKS)
        right = self._compute_ear(landmarks, RIGHT_EYE_LANDMARKS)
        return (left + right) / 2.0

    def _mouth_ratio(self, landmarks) -> float:
        left_corner = landmarks[MOUTH_LANDMARKS[0]]
        right_corner = landmarks[MOUTH_LANDMARKS[1]]
        top = landmarks[MOUTH_LANDMARKS[2]]
        bottom = landmarks[MOUTH_LANDMARKS[3]]

        horizontal = self._distance(left_corner, right_corner)
        vertical = self._distance(top, bottom)
        if vertical == 0:
            return 0.0
        return horizontal / vertical

    def _attention_estimate(self, landmarks) -> tuple[bool, float]:
        """Estimate whether the user is looking away based on nose placement."""
        nose = landmarks[NOSE_TIP_LANDMARK]
        offset = abs(nose.x - 0.5)
        looking_away = offset > self.config.look_away_threshold
        normalized = min(offset / self.config.look_away_threshold, 1.0) if self.config.look_away_threshold else 0.0
        attention_score = max(0.0, 1.0 - normalized)
        return looking_away, attention_score

    def _compute_ear(self, landmarks, indices: tuple[int, int, int, int]) -> float:
        horizontal = self._distance(landmarks[indices[0]], landmarks[indices[1]])
        vertical = self._distance(landmarks[indices[2]], landmarks[indices[3]])
        if horizontal == 0:
            return 0.0
        return vertical / horizontal

    @staticmethod
    def _distance(a, b) -> float:
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


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
