from src.services.video_analytics_service import (
    EngagementMetrics,
    EngagementStateTracker,
)


def make_metrics(**overrides) -> EngagementMetrics:
    base = dict(
        timestamp=1.0,
        user_id="test-user",
        face_detected=True,
        attention_score=0.9,
        looking_away=False,
        eyes_closed=False,
        eye_aspect_ratio=0.2,
        smile_score=1.0,
        is_smiling=False,
        frame_size=(640, 360),
    )
    base.update(overrides)
    return EngagementMetrics(**base)


def test_tracker_emits_attention_and_smile_events():
    tracker = EngagementStateTracker(min_event_gap_secs=0.0)

    # Initial metrics transition the tracker out of the "unknown" state.
    events = tracker.update(make_metrics(timestamp=1.0))
    assert events and events[0].type == "attention"
    assert "re-engaged" in events[0].summary

    # Looking away triggers a disengagement event.
    events = tracker.update(make_metrics(timestamp=2.0, looking_away=True, attention_score=0.1))
    assert events and events[0].payload["reason"] == "looking away from the screen"

    # Returning to attentive while smiling emits both attention + smile events.
    events = tracker.update(
        make_metrics(timestamp=3.0, looking_away=False, attention_score=0.8, is_smiling=True, smile_score=2.2)
    )
    event_types = {event.type for event in events}
    assert {"attention", "smile"} == event_types


def test_tracker_throttles_events():
    tracker = EngagementStateTracker(min_event_gap_secs=5.0)

    # Initial event suppressed because not enough time has elapsed.
    events = tracker.update(make_metrics(timestamp=1.0))
    assert not events

    # Changing state before the debounce window should not emit again.
    events = tracker.update(make_metrics(timestamp=2.0, eyes_closed=True))
    assert not events

    # After cooldown, returning to attentive emits an event.
    events = tracker.update(make_metrics(timestamp=7.5, eyes_closed=False))
    assert events and events[0].type == "attention"

    # Rapidly changing back to distracted is throttled.
    events = tracker.update(make_metrics(timestamp=9.0, eyes_closed=True))
    assert not events

    # Waiting long enough allows additional events in both directions.
    events = tracker.update(make_metrics(timestamp=14.5, eyes_closed=False))
    assert events and events[0].type == "attention"
    events = tracker.update(make_metrics(timestamp=20.0, eyes_closed=True))
    assert events and events[0].type == "attention"
