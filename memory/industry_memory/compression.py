"""
Domain-Aware Compression

Preserves structural constraints (entity fields, timeline order,
inventory counts) while compressing narrative text.

Rules:
  - Lossless: numeric fields, dates, statuses, IDs, vendor ratings
  - Lossy:  customer narrative, call small-talk, email signatures
  - Semantic: preserve sentences containing entity transitions
"""

import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class DomainAwareCompressor:
    """
    Compress transcripts and entity documents while preserving
domain-critical information.
    """

    # Sentences that MUST be preserved (contain state transitions)
    TRANSITION_TRIGGERS = [
        r"\b(?:approved|accepted|signed|agreed to)\b",
        r"\b(?:rejected|declined|went with someone else|too expensive)\b",
        r"\b(?:started|began work|crew arrived|materials delivered)\b",
        r"\b(?:finished|completed|done|inspection passed)\b",
        r"\b(?:invoice sent|payment received|check cleared)\b",
        r"\b(?:permit approved|inspection scheduled|failed inspection)\b",
        r"\b(?:delay|postponed|rescheduled|weather hold)\b",
    ]

    # Content that can be stripped entirely
    NOISE_PATTERNS = [
        r"^\s*On .* wrote:.*",  # email headers
        r"^\s*>.*",  # quoted lines
        r"\-\-\-.*?\-\-",  # signature dividers
        r"Sent from my iPhone.*",
        r"Best regards.*",
        r"Thanks,?\s*(?:\n|$)",
        r"\b(unsubscribe|privacy policy|view in browser)\b",
    ]

    # Fields that must never be compressed
    PRESERVE_FIELDS = {
        "lead_id", "estimate_id", "job_id", "vendor_id", "material_id",
        "total", "unit_cost", "quantity_on_hand", "quantity_ordered",
        "lat", "lng", "zip_code", "phone", "email",
        "status", "stage", "priority", "urgency",
        "start_date", "target_completion", "actual_completion",
        "permit_status", "inspection_status",
    }

    def __init__(self, max_narrative_chars: int = 400):
        self.max_narrative_chars = max_narrative_chars

    def compress_entity(self, entity_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress an entity dictionary.

        Numeric/enum fields preserved verbatim.
        Text fields (notes, transcripts) compressed narratively.
        """
        compressed = {}
        for key, value in entity_dict.items():
            if key in self.PRESERVE_FIELDS:
                compressed[key] = value
            elif isinstance(value, str) and len(value) > self.max_narrative_chars:
                compressed[key] = self._compress_text(value)
            elif isinstance(value, dict):
                compressed[key] = self.compress_entity(value)
            elif isinstance(value, list):
                compressed[key] = [
                    self.compress_entity(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                compressed[key] = value
        return compressed

    def compress_transcript(self, text: str) -> str:
        """Compress a raw transcript, preserving transition sentences."""
        # Strip noise patterns
        lines = text.splitlines()
        clean_lines = []
        for line in lines:
            if any(re.search(pat, line, re.I) for pat in self.NOISE_PATTERNS):
                continue
            clean_lines.append(line)

        text = "\n".join(clean_lines)

        # Identify transition sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        preserved = []
        discarded = []

        for sent in sentences:
            if self._is_transition_sentence(sent):
                preserved.append(sent)
            elif len(sent.strip()) > 10:
                discarded.append(sent)

        # Reconstruct: transitions first, then summary of discarded
        result = " ".join(preserved)
        if discarded:
            summary = self._summarize_discarded(discarded)
            if summary:
                result += f" [OTHER: {summary}]"

        return result[: self.max_narrative_chars]

    def compress_timeline(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compress a timeline by collapsing adjacent non-transition events
        into a single summary entry.
        """
        if not events:
            return []

        compressed = []
        buffer = [events[0]]

        for event in events[1:]:
            if self._is_transition_event(event):
                if len(buffer) > 1:
                    compressed.append(self._collapse_buffer(buffer))
                else:
                    compressed.extend(buffer)
                buffer = [event]
            else:
                buffer.append(event)

        if len(buffer) > 1:
            compressed.append(self._collapse_buffer(buffer))
        else:
            compressed.extend(buffer)

        return compressed

    def _is_transition_sentence(self, sentence: str) -> bool:
        return any(re.search(pat, sentence, re.I) for pat in self.TRANSITION_TRIGGERS)

    def _is_transition_event(self, event: Dict[str, Any]) -> bool:
        text = event.get("document", "") + " " + json.dumps(event.get("metadata", {}))
        return self._is_transition_sentence(text)

    def _summarize_discarded(self, sentences: List[str]) -> str:
        # Very lightweight: return count + first 80 chars
        combined = " ".join(s.strip() for s in sentences if s.strip())
        if not combined:
            return ""
        return f"{len(sentences)} sentences; {combined[:80]}..."

    def _collapse_buffer(self, buffer: List[Dict[str, Any]]) -> Dict[str, Any]:
        start = buffer[0]
        end = buffer[-1]
        return {
            "id": f"collapsed_{start['id']}_{end['id']}",
            "document": f"[{len(buffer)} routine events from {start.get('metadata', {}).get('ts', '?')} to {end.get('metadata', {}).get('ts', '?')} ]",
            "metadata": {
                "collapsed_count": len(buffer),
                "start_ts": start.get("metadata", {}).get("ts"),
                "end_ts": end.get("metadata", {}).get("ts"),
                "event_types": list({e.get("metadata", {}).get("event_type") for e in buffer}),
            },
        }

    def _compress_text(self, text: str) -> str:
        # If it looks like a transcript, use transcript compression
        if len(text) > 200 and "\n" in text:
            return self.compress_transcript(text)
        # Otherwise just truncate
        return text[: self.max_narrative_chars]
