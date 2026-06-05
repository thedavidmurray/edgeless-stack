#!/usr/bin/env python3
"""
Demo: Local Service Memory Kernel — Roofing Contractor

Shows the full flow:
  1. Register a client
  2. Ingest SMS/email/call transcripts
  3. Extract structured leads
  4. Compress domain-aware
  5. Store in isolated ChromaDB collections
  6. Search and timeline replay

Run:
    cd /Users/djm/claude-projects/edgeless-stack/memory
    python3 -m industry_memory.demo_contractor
"""

import json
import sys
from datetime import datetime

sys.path.insert(0, "/Users/djm/claude-projects/edgeless-stack/memory")

from industry_memory.taxonomy import (
    Contact,
    Address,
    LeadStage,
    JobStatus,
    Priority,
    LocalServiceTaxonomy,
)
from industry_memory.schema import ClientMemorySchema
from industry_memory.ingestion import TranscriptIngestionPipeline
from industry_memory.compression import DomainAwareCompressor


def demo_without_chroma():
    print("=" * 60)
    print("LOCAL SERVICE MEMORY KERNEL DEMO")
    print("Client: Murray Roofing & Remodeling")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Taxonomy: create entities
    # ------------------------------------------------------------------
    print("\n[1] ENTITY CREATION")
    contact = Contact(name="Sarah Jenkins", phone="+15559876543", email="sarah.j@example.com")
    address = Address(street="4521 Maple Ave", city="Springfield", state="IL", zip_code="62704")
    lead = LocalServiceTaxonomy.create_lead(
        lead_id="lead_001",
        contact=contact,
        address=address,
        project_type="roof_replacement",
        source_channel="sms",
    )
    print(f"  Lead created: {lead.id}")
    print(f"    Contact: {lead.contact.name} / {lead.contact.phone}")
    print(f"    Address: {lead.address.street}, {lead.address.city} {lead.address.state}")
    print(f"    Project: {lead.project_type} | Stage: {lead.stage.name} | Urgency: {lead.urgency.name}")

    # ------------------------------------------------------------------
    # 2. Ingestion pipeline
    # ------------------------------------------------------------------
    print("\n[2] INGESTION PIPELINE")
    pipeline = TranscriptIngestionPipeline(client_slug="murray_roofing")

    sms_text = (
        "Hi this is Mike from 7820 Oakridge Dr, Springfield IL 62704. "
        "We had bad hail last night and I think our roof is damaged. "
        "Can someone come out ASAP? My number is 555-234-5678. "
        "Email: mike.rodriguez@email.com"
    )
    lead2 = pipeline.ingest_sms(text=sms_text, phone="+15552345678")
    if lead2:
        print(f"  SMS lead extracted: {lead2.id}")
        print(f"    Name: {lead2.contact.name} | Project: {lead2.project_type} | Urgency: {lead2.urgency.name}")
    else:
        print("  SMS: no address found (would store as raw transcript)")

    email_body = (
        "Hello,\n\n"
        "My name is Jennifer Walsh. We live at 3310 Riverbend Blvd, Springfield IL 62704. "
        "We're looking to replace the siding on our two-story home. "
        "Please send an estimate when convenient.\n\n"
        "Best regards,\n"
        "Jennifer Walsh\n"
        "jwalsh.home@email.com\n"
        "Sent from my iPhone"
    )
    lead3 = pipeline.ingest_email(
        subject="Estimate request for siding replacement",
        body=email_body,
        from_email="jwalsh.home@email.com",
    )
    if lead3:
        print(f"  Email lead extracted: {lead3.id}")
        print(f"    Name: {lead3.contact.name} | Project: {lead3.project_type}")
    else:
        print("  Email: no address found")

    call_transcript = (
        "Agent: Thanks for calling Murray Roofing. How can I help?\n"
        "Caller: Hi, this is David. We have an active leak in our kitchen ceiling. "
        "Address is 1200 Forest Hills Rd, Springfield IL 62704. "
        "Can you send someone today? It's an emergency.\n"
        "Agent: Absolutely, let me get your info."
    )
    lead4 = pipeline.ingest_call_transcript(
        transcript=call_transcript,
        caller_number="+15555678901",
    )
    if lead4:
        print(f"  Call lead extracted: {lead4.id}")
        print(f"    Name: {lead4.contact.name} | Urgency: {lead4.urgency.name}")

    # ------------------------------------------------------------------
    # 3. Stage transition
    # ------------------------------------------------------------------
    print("\n[3] STATE TRANSITIONS")
    LocalServiceTaxonomy.stage_transition(lead, LeadStage.ESTIMATE_SCHEDULED)
    print(f"  Lead {lead.id} stage: {lead.stage.name}")
    print(f"    Tags: {lead.tags}")

    job = LocalServiceTaxonomy.create_job_from_estimate(
        job_id="job_001",
        estimate_id="est_001",
        lead_id=lead.id,
        crew_assigned="Crew A",
    )
    print(f"  Job created: {job.id} | Status: {job.status.name} | Crew: {job.crew_assigned}")
    LocalServiceTaxonomy.job_status_transition(job, JobStatus.IN_PROGRESS)
    print(f"  Job status updated: {job.status.name}")
    print(f"    Tags: {job.tags}")

    # ------------------------------------------------------------------
    # 4. Compression
    # ------------------------------------------------------------------
    print("\n[4] DOMAIN-AWARE COMPRESSION")
    compressor = DomainAwareCompressor(max_narrative_chars=300)

    long_note = (
        "Customer called at 8am very stressed about water coming through the ceiling. "
        "They tried to put a bucket under it but it's spreading. They have a newborn "
        "in the house and are worried about mold. Previous roofer never returned calls. "
        "They saw our truck in the neighborhood and decided to try us. "
        "Wants us to start as soon as possible. Budget is flexible but wants itemized estimate. "
        "Mentioned they might need gutters too but that's secondary."
    )
    compressed = compressor.compress_transcript(long_note)
    print(f"  Original: {len(long_note)} chars")
    print(f"  Compressed: {len(compressed)} chars")
    print(f"  Text: {compressed}")

    # ------------------------------------------------------------------
    # 5. Schema overview
    # ------------------------------------------------------------------
    print("\n[5] CLIENT SCHEMA")
    schema = ClientMemorySchema("Murray Roofing")
    print(f"  Client slug: {schema.client_slug}")
    print("  Collections:")
    for key, spec in schema.to_dict()["collections"].items():
        print(f"    - {key}: {spec['name']}")
        print(f"      {spec['description']}")

    # ------------------------------------------------------------------
    # 6. Ingestion log
    # ------------------------------------------------------------------
    print("\n[6] INGESTION LOG")
    for entry in pipeline.get_log():
        print(f"  {entry['ts'][:19]} | {entry['channel']:6} | {entry['type']} | {entry.get('lead_id', 'N/A')}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_without_chroma()
