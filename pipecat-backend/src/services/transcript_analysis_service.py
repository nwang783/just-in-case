"""
Utilities for analyzing finished transcripts with OpenAI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger
from openai import OpenAI


class TranscriptAnalyzer:
    """Analyze saved transcripts and persist structured insights."""

    RESPONSE_SCHEMA: Dict[str, Any] = {
        "name": "TranscriptAnalysis",
        "schema": {
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string"},
                "case_summary": {
                    "type": "object",
                    "properties": {
                        "case_type": {"type": "string"},
                        "overall_summary": {"type": "string"},
                        "user_confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                    "required": ["case_type", "overall_summary", "user_confidence"],
                    "additionalProperties": False,
                },
                "key_events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timestamp": {"type": "string"},
                            "speaker": {"type": "string", "enum": ["user", "assistant"]},
                            "message": {"type": "string"},
                        },
                        "required": ["timestamp", "speaker", "message"],
                        "additionalProperties": False,
                    },
                    "maxItems": 6,
                },
                "coaching_feedback": {
                    "type": "object",
                    "properties": {
                        "strengths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 5,
                        },
                        "areas_for_improvement": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 5,
                        },
                        "next_practice_focus": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 5,
                        },
                    },
                    "required": ["strengths", "areas_for_improvement", "next_practice_focus"],
                    "additionalProperties": False,
                },
                "action_items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 5,
                },
                "sentiment": {
                    "type": "object",
                    "properties": {
                        "user": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                        "assistant": {
                            "type": "string",
                            "enum": ["supportive", "neutral", "critical"],
                        },
                    },
                    "required": ["user", "assistant"],
                    "additionalProperties": False,
                },
            },
            "required": [
                "conversation_id",
                "case_summary",
                "key_events",
                "coaching_feedback",
                "action_items",
                "sentiment",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    }

    def __init__(self, model: str, output_dir: Path):
        self.client = OpenAI()
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
        prompt = self._build_prompt(entries)

        logger.info(f"Analyzing transcript {conversation_id} with model {self.model}")
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            response_format={"type": "json_schema", "json_schema": self.RESPONSE_SCHEMA},
            temperature=0.2,
        )

        analysis_payload = self._extract_json(response)
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

    def _build_prompt(self, entries: List[Dict[str, Any]]) -> str:
        content = {
            "instructions": (
                "You are an expert case interview coach. "
                "Review the provided transcript and return concise, structured insights "
                "that help a coach understand how the session went."
            ),
            "transcript": entries,
            "analysis_goals": [
                "Identify the case type and summarize the flow.",
                "Highlight important conversational moments (questions, hypotheses, numbers).",
                "Provide coach-ready feedback focused on the candidate.",
                "List actionable practice items for the candidate.",
                "Assess sentiment/energy for both participants.",
            ],
        }
        return json.dumps(content, ensure_ascii=False)

    def _extract_json(self, response) -> Dict[str, Any]:
        output_items = getattr(response, "output", None) or []
        for item in output_items:
            content_items = getattr(item, "content", None) or []
            for piece in content_items:
                payload = None
                if hasattr(piece, "text") and piece.text:
                    payload = piece.text
                elif hasattr(piece, "json") and piece.json:
                    payload = json.dumps(piece.json)
                if payload:
                    try:
                        return json.loads(payload)
                    except json.JSONDecodeError:
                        continue
        raise ValueError("OpenAI response did not contain JSON output")
