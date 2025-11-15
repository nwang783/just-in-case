import json
import os
import time
from pathlib import Path

from src.services.analysis_repository import AnalysisRepository


def _write_transcript(transcripts_dir: Path, conversation_id: str) -> Path:
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    path = transcripts_dir / f"{conversation_id}.jsonl"
    payload = {
        "type": "metadata",
        "conversation_id": conversation_id,
    }
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def _write_analysis(analysis_dir: Path, conversation_id: str, transcript_path: Path) -> Path:
    analysis_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "conversation_id": conversation_id,
        "case_summary": {
            "case_type": "Retail profit",
            "overall_summary": "Summary text",
            "user_confidence": "medium",
        },
        "key_events": [
            {"timestamp": "2024-01-01T00:00:00Z", "speaker": "User", "message": "Hi"}
        ],
        "coaching_feedback": {
            "strengths": ["Engaged"],
            "areas_for_improvement": ["Add structure"],
            "next_practice_focus": ["Mock interviews"],
        },
        "action_items": ["Practice more"],
        "sentiment": {"user": "neutral", "assistant": "supportive"},
        "engagement_summary": {"summary": "Good focus."},
        "source_transcript": str(transcript_path),
    }
    path = analysis_dir / f"{conversation_id}-analysis.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_get_status_pending_when_analysis_missing(tmp_path):
    transcripts_dir = tmp_path / "transcripts"
    analysis_dir = tmp_path / "analysis"
    conversation_id = "conversation-123"
    _write_transcript(transcripts_dir, conversation_id)

    repo = AnalysisRepository(transcripts_dir=transcripts_dir, analysis_dir=analysis_dir)
    status = repo.get_status(conversation_id)

    assert status is not None
    assert status.status == "pending"
    assert status.conversation_id == conversation_id
    assert status.analysis is None


def test_get_status_ready_when_analysis_available(tmp_path):
    transcripts_dir = tmp_path / "transcripts"
    analysis_dir = tmp_path / "analysis"
    conversation_id = "conversation-abc"
    transcript_path = _write_transcript(transcripts_dir, conversation_id)
    _write_analysis(analysis_dir, conversation_id, transcript_path)

    repo = AnalysisRepository(transcripts_dir=transcripts_dir, analysis_dir=analysis_dir)
    status = repo.get_status(conversation_id)

    assert status is not None
    assert status.status == "ready"
    assert status.conversation_id == conversation_id
    assert status.analysis is not None
    assert status.analysis.case_summary.case_type == "Retail profit"


def test_list_ready_analyses_returns_latest_first(tmp_path):
    transcripts_dir = tmp_path / "transcripts"
    analysis_dir = tmp_path / "analysis"

    repo = AnalysisRepository(transcripts_dir=transcripts_dir, analysis_dir=analysis_dir)
    base_time = time.time()

    for index in range(3):
        conversation_id = f"conversation-{index}"
        transcript_path = _write_transcript(transcripts_dir, conversation_id)
        analysis_file = _write_analysis(analysis_dir, conversation_id, transcript_path)
        os.utime(analysis_file, (base_time + index, base_time + index))

    summaries = repo.list_analyses(limit=2)
    assert len(summaries) == 2
    assert summaries[0].conversation_id == "conversation-2"
    assert summaries[1].conversation_id == "conversation-1"


def test_list_analyses_can_include_pending(tmp_path):
    transcripts_dir = tmp_path / "transcripts"
    analysis_dir = tmp_path / "analysis"
    repo = AnalysisRepository(transcripts_dir=transcripts_dir, analysis_dir=analysis_dir)

    transcript_ready = _write_transcript(transcripts_dir, "conversation-ready")
    _write_analysis(analysis_dir, "conversation-ready", transcript_ready)
    _write_transcript(transcripts_dir, "conversation-pending")

    summaries = repo.list_analyses(limit=5, include_pending=True)
    assert len(summaries) == 2
    assert {item.conversation_id for item in summaries} == {
        "conversation-ready",
        "conversation-pending",
    }
    pending = next(item for item in summaries if item.conversation_id.endswith("pending"))
    assert pending.status == "pending"
