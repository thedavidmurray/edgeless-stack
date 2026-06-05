"""
Transcript Ingestion Pipeline

Cron-friendly ingestion from SMS, email, and phone call transcripts.
Maps unstructured text to structured taxonomy entities.
"""

import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import os

from .taxonomy import (
    LocalServiceTaxonomy,
    Contact,
    Address,
    Lead,
    LeadStage,
    Priority,
    EntityType,
)


class TranscriptIngestionPipeline:
    """
    Ingest raw transcripts and extract structured entities.

    Usage:
        pipeline = TranscriptIngestionPipeline(client_slug="murray_roofing")
        lead = pipeline.ingest_sms(
            text="Hi this is John from 123 Oak St. We had hail damage and need a roof estimate ASAP.",
            phone="+15551234567",
            timestamp=datetime.now(),
        )
    """

    # Regex patterns for entity extraction (lightweight, no LLM required)
    ADDRESS_PATTERNS = [
        r"(\d+\s+[\w\s]+(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Ln|Lane|Ct|Court|Blvd|Boulevard|Way|Pl|Place|Trail|Cir|Circle)\b)",
    ]
    PHONE_PATTERN = r"(\+?1?\s?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
    EMAIL_PATTERN = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    URGENCY_KEYWORDS = {
        Priority.EMERGENCY: ["emergency", "leaking", "active leak", "water damage", "collapse", "falling"],
        Priority.URGENT: ["asap", "urgent", "this week", "before", "storm coming", "inspection deadline"],
        Priority.HIGH: ["soon", "quickly", "fast", "hail damage", "wind damage"],
    }
    PROJECT_TYPE_KEYWORDS = {
        "roof_repair": ["repair", "patch", "leak", "missing shingle", "small fix"],
        "roof_replacement": ["new roof", "full replacement", "replace", "entire roof", "re-roof"],
        "siding": ["siding", "vinyl siding", "hardie board"],
        "gutters": ["gutters", "downspout", "gutter guard"],
        "remodel": ["remodel", "renovation", "kitchen", "bathroom", "addition"],
    }

    def __init__(self, client_slug: str, callback: Optional[Callable[[Lead], None]] = None):
        self.client_slug = client_slug
        self.callback = callback
        self._ingestion_log: List[Dict[str, Any]] = []

    def ingest_sms(
        self,
        text: str,
        phone: str,
        timestamp: Optional[datetime] = None,
        thread_id: Optional[str] = None,
    ) -> Optional[Lead]:
        """Ingest an SMS message and extract a Lead if possible."""
        if not timestamp:
            timestamp = datetime.now()

        # Extract entities
        name = self._extract_name(text)
        address = self._extract_address(text)
        email = self._extract_email(text)
        project_type = self._detect_project_type(text)
        urgency = self._detect_urgency(text)

        if not address:
            # SMS without address — store as raw transcript, don't create lead yet
            self._log_raw("sms", text, phone, timestamp, thread_id)
            return None

        lead_id = self._make_id(text, phone, timestamp)
        contact = Contact(name=name or "Unknown", phone=phone, email=email)

        lead = LocalServiceTaxonomy.create_lead(
            lead_id=lead_id,
            contact=contact,
            address=address,
            project_type=project_type or "unknown",
            source_channel="sms",
            urgency=urgency,
        )
        lead.raw_transcript_ref = thread_id or f"sms:{phone}:{timestamp.isoformat()}"
        lead.notes = text

        self._log_ingestion(lead)
        if self.callback:
            self.callback(lead)
        return lead

    def ingest_email(
        self,
        subject: str,
        body: str,
        from_email: str,
        timestamp: Optional[datetime] = None,
        thread_id: Optional[str] = None,
    ) -> Optional[Lead]:
        """Ingest an email and extract a Lead if possible."""
        if not timestamp:
            timestamp = datetime.now()

        full_text = f"{subject}\n{body}"
        name = self._extract_name(full_text) or self._extract_name_from_email(from_email)
        address = self._extract_address(full_text)
        phone = self._extract_phone(full_text)
        project_type = self._detect_project_type(full_text)
        urgency = self._detect_urgency(full_text)

        if not address:
            self._log_raw("email", full_text, from_email, timestamp, thread_id)
            return None

        lead_id = self._make_id(full_text, from_email, timestamp)
        contact = Contact(name=name or "Unknown", phone=phone, email=from_email)

        lead = LocalServiceTaxonomy.create_lead(
            lead_id=lead_id,
            contact=contact,
            address=address,
            project_type=project_type or "unknown",
            source_channel="email",
            urgency=urgency,
        )
        lead.raw_transcript_ref = thread_id or f"email:{from_email}:{timestamp.isoformat()}"
        lead.notes = full_text[:500]  # truncate for storage

        self._log_ingestion(lead)
        if self.callback:
            self.callback(lead)
        return lead

    def ingest_call_transcript(
        self,
        transcript: str,
        caller_number: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        call_id: Optional[str] = None,
    ) -> Optional[Lead]:
        """Ingest a phone call transcript."""
        if not timestamp:
            timestamp = datetime.now()

        name = self._extract_name(transcript)
        address = self._extract_address(transcript)
        phone = caller_number or self._extract_phone(transcript)
        email = self._extract_email(transcript)
        project_type = self._detect_project_type(transcript)
        urgency = self._detect_urgency(transcript)

        if not address:
            self._log_raw("call", transcript, caller_number or "unknown", timestamp, call_id)
            return None

        lead_id = self._make_id(transcript, caller_number or "", timestamp)
        contact = Contact(name=name or "Unknown", phone=phone, email=email)

        lead = LocalServiceTaxonomy.create_lead(
            lead_id=lead_id,
            contact=contact,
            address=address,
            project_type=project_type or "unknown",
            source_channel="phone",
            urgency=urgency,
        )
        lead.raw_transcript_ref = call_id or f"call:{caller_number}:{timestamp.isoformat()}"
        lead.notes = transcript[:500]

        self._log_ingestion(lead)
        if self.callback:
            self.callback(lead)
        return lead

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_name(self, text: str) -> Optional[str]:
        # Simple heuristic: "This is [Name]" or "My name is [Name]"
        m = re.search(r"(?:this is|my name is|i am|name[\s:]+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text, re.I)
        if m:
            return m.group(1).strip()
        return None

    def _extract_name_from_email(self, email: str) -> Optional[str]:
        local = email.split("@")[0]
        parts = re.split(r"[._\-]", local)
        if parts:
            return " ".join(p.capitalize() for p in parts if p.isalpha())
        return None

    def _extract_address(self, text: str) -> Optional[Address]:
        # Very lightweight — in production, use a geocoding API or USPS validator
        for pattern in self.ADDRESS_PATTERNS:
            m = re.search(pattern, text, re.I)
            if m:
                street = m.group(1).strip()
                # City/State/ZIP heuristic: look for "City, ST 12345" after street
                tail = text[m.end():m.end()+100]
                city_state_zip = re.search(r"([A-Za-z\s]+),?\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", tail)
                if city_state_zip:
                    return Address(
                        street=street,
                        city=city_state_zip.group(1).strip(),
                        state=city_state_zip.group(2),
                        zip_code=city_state_zip.group(3),
                    )
                return Address(street=street, city="", state="", zip_code="")
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        m = re.search(self.PHONE_PATTERN, text)
        return m.group(1) if m else None

    def _extract_email(self, text: str) -> Optional[str]:
        m = re.search(self.EMAIL_PATTERN, text)
        return m.group(1) if m else None

    def _detect_project_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        scores = {}
        for ptype, keywords in self.PROJECT_TYPE_KEYWORDS.items():
            scores[ptype] = sum(1 for kw in keywords if kw in text_lower)
        if scores:
            best = max(scores, key=scores.get)
            if scores[best] > 0:
                return best
        return None

    def _detect_urgency(self, text: str) -> Priority:
        text_lower = text.lower()
        for priority, keywords in self.URGENCY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return priority
        return Priority.NORMAL

    def _make_id(self, *parts: Any) -> str:
        """Deterministic ID from content + phone + timestamp."""
        payload = "|".join(str(p) for p in parts)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _log_raw(self, channel: str, text: str, identifier: str, timestamp: datetime, thread_id: Optional[str]) -> None:
        self._ingestion_log.append({
            "ts": timestamp.isoformat(),
            "channel": channel,
            "type": "raw",
            "identifier": identifier,
            "thread_id": thread_id,
            "text_preview": text[:200],
            "extracted": False,
        })

    def _log_ingestion(self, lead: Lead) -> None:
        self._ingestion_log.append({
            "ts": datetime.now().isoformat(),
            "channel": lead.source_channel,
            "type": "lead_extracted",
            "lead_id": lead.id,
            "project_type": lead.project_type,
            "urgency": lead.urgency.name,
            "stage": lead.stage.name,
        })

    def get_log(self) -> List[Dict[str, Any]]:
        return self._ingestion_log

    def write_log(self, path: str) -> None:
        with open(path, "a") as f:
            for entry in self._ingestion_log:
                f.write(json.dumps(entry) + "\n")
        self._ingestion_log.clear()
