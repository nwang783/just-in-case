"""
Utilities for analyzing finished transcripts with OpenAI Structured Outputs.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel, Field, conlist


class KeyEvent(BaseModel):
    timestamp: Optional[str] = None
    speaker: str
    message: str


class CaseSummary(BaseModel):
    case_type: str
    overall_summary: str
    user_confidence: Literal["high", "medium", "low"]


class CoachingFeedback(BaseModel):
    strengths: conlist(str, max_length=5) = Field(default_factory=list)
    areas_for_improvement: conlist(str, max_length=5) = Field(default_factory=list)
    next_practice_focus: conlist(str, max_length=5) = Field(default_factory=list)


class Sentiment(BaseModel):
    user: Literal["positive", "neutral", "negative"]
    assistant: Literal["supportive", "neutral", "critical"]


class EngagementSummary(BaseModel):
    """High-level interpretation of the user's non-verbal engagement."""

    summary: str = Field(
        default="",
        description="Narrative summary about the candidate's engagement, referencing vision analytics.",
    )


class TranscriptAnalysisResult(BaseModel):
    conversation_id: str
    case_summary: CaseSummary
    key_events: conlist(KeyEvent, max_length=6) = Field(default_factory=list)
    coaching_feedback: CoachingFeedback
    action_items: conlist(str, max_length=5) = Field(default_factory=list)
    sentiment: Sentiment
    engagement_summary: EngagementSummary = Field(default_factory=EngagementSummary)


class TranscriptAnalyzer:
    """Analyze saved transcripts and persist structured insights."""

    def __init__(self, model: str, output_dir: Path, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, transcript_path: Path) -> Path:
        """
        Run OpenAI analysis over the transcript JSONL file and persist results.

        Args:
            transcript_path: Path to the transcript JSONL file.

        Returns:
            Path to the structured analysis JSON file.
        """
        entries = self._load_entries(transcript_path)
        if not entries:
            raise ValueError(f"No transcript entries found at {transcript_path}")

        conversation_id = self._extract_conversation_id(entries)
        prompt = self._build_prompt(entries, conversation_id)

        logger.info(f"Analyzing transcript {conversation_id} with model {self.model}")
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "You are a case interview coach that summarizes transcripts into structured coaching insights.",
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt, ensure_ascii=False),
                },
            ],
            text_format=TranscriptAnalysisResult,
        )

        refusal_reason = self._extract_refusal(response)
        if refusal_reason:
            raise RuntimeError(f"Transcript analysis refused by model: {refusal_reason}")

        analysis_model = getattr(response, "output_parsed", None)
        if not analysis_model:
            raise ValueError("OpenAI response did not include parsed output")

        analysis_payload = analysis_model.model_dump()
        analysis_payload["conversation_id"] = conversation_id
        analysis_payload["source_transcript"] = str(transcript_path)

        output_path = self.output_dir / f"{transcript_path.stem}-analysis.json"
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(analysis_payload, fh, ensure_ascii=False, indent=2)

        logger.info(f"Transcript analysis saved to {output_path}")
        return output_path

    def _load_entries(self, transcript_path: Path) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        with transcript_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    entries.append(json.loads(line))
        return entries

    def _extract_conversation_id(self, entries: List[Dict[str, Any]]) -> str:
        for entry in entries:
            convo_id = entry.get("conversation_id")
            if convo_id:
                return convo_id
        raise ValueError("Transcript missing conversation_id")

    def _build_prompt(self, entries: List[Dict[str, Any]], conversation_id: str) -> Dict[str, Any]:
        vision_summary = self._summarize_vision_events(entries)
        return {
            "instructions": (
                "Review the transcript from the perspective of a case interview coach. "
                "Focus solely on evaluating the candidate (user)—not the coach/assistant. "
                "Populate every field with concise, user-facing insights and avoid repeating prompts verbatim."
            ),
            "conversation_id": conversation_id,
            "transcript": entries,
            "analysis_goals": [
                "Determine the case type and summarize the candidate's approach.",
                "Highlight candidate actions (e.g., clarifying questions, hypotheses, calculations).",
                "List candidate strengths, areas to improve, and next practice focuses.",
                "Provide 1–5 action items tailored to the candidate.",
                "Assess sentiment for the candidate and the assistant's tone.",
                "Leverage the provided vision analytics summary when commenting on engagement, confidence, or non-verbal cues.",
            ],
            "vision_analytics": vision_summary,
        }

    def _extract_refusal(self, response) -> Optional[str]:
        for item in getattr(response, "output", []) or []:
            for piece in getattr(item, "content", []) or []:
                if getattr(piece, "type", None) == "refusal":
                    return getattr(piece, "refusal", "Unknown reason")
        return None

    @staticmethod
    def _summarize_vision_events(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate engagement events emitted by the vision analytics processor."""
        summary = {
            "total_events": 0,
            "attention_events": 0,
            "attention_regained_events": 0,
            "attention_drop_reasons": [],
            "smile_events": 0,
            "smile_start_events": 0,
            "smile_stop_events": 0,
            "example_notes": [],
        }

        reasons = Counter()
        example_notes: List[str] = []
        for entry in entries:
            if entry.get("type") != "event" or entry.get("event") != "vision":
                continue

            summary["total_events"] += 1
            metadata = entry.get("metadata", {}) or {}
            note = entry.get("text") or ""
            if note:
                example_notes.append(note)

            event_type = metadata.get("event_type")
            if event_type == "attention":
                summary["attention_events"] += 1
                reason = metadata.get("reason")
                if reason:
                    reasons[reason] += 1
                else:
                    summary["attention_regained_events"] += 1
            elif event_type == "smile":
                summary["smile_events"] += 1
                if metadata.get("smiling"):
                    summary["smile_start_events"] += 1
                else:
                    summary["smile_stop_events"] += 1

        if reasons:
            summary["attention_drop_reasons"] = [
                {"reason": reason, "count": count} for reason, count in reasons.most_common()
            ]

        if example_notes:
            summary["example_notes"] = example_notes[:10]

        return summary
