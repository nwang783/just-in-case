from src.services.transcript_analysis_service import TranscriptAnalyzer


def test_summarize_vision_events_counts_reasons():
    entries = [
        {"type": "message", "role": "user", "text": "hello"},
        {
            "type": "event",
            "event": "vision",
            "text": "User disengaged or lost attention (eyes closed).",
            "metadata": {"event_type": "attention", "reason": "eyes closed"},
        },
        {
            "type": "event",
            "event": "vision",
            "text": "User re-engaged with the interview (attention 0.90).",
            "metadata": {"event_type": "attention"},
        },
        {
            "type": "event",
            "event": "vision",
            "text": "User started smiling (score 2.10)",
            "metadata": {"event_type": "smile", "smiling": True},
        },
        {
            "type": "event",
            "event": "vision",
            "text": "User stopped smiling.",
            "metadata": {"event_type": "smile", "smiling": False},
        },
    ]

    summary = TranscriptAnalyzer._summarize_vision_events(entries)

    assert summary["total_events"] == 4
    assert summary["attention_events"] == 2
    assert summary["attention_regained_events"] == 1
    assert summary["smile_events"] == 2
    assert summary["smile_start_events"] == 1
    assert summary["smile_stop_events"] == 1
    assert summary["attention_drop_reasons"] == [{"reason": "eyes closed", "count": 1}]
    assert len(summary["example_notes"]) == 4
    assert "Detected 2 attention-related events" in summary["narrative"]
