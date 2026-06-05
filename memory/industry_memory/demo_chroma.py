#!/usr/bin/env python3
"""
End-to-End Demo: Local Service Memory Kernel with ChromaDB

Shows the full production flow:
  1. Connect to ChromaDB
  2. Register a client (tenant isolation)
  3. Ingest SMS / email / call transcripts
  4. Extract structured leads
  5. Compress domain-aware
  6. Store in isolated ChromaDB collections
  7. Semantic search across client memory
  8. Timeline replay
  9. Cleanup

Run:
    cd /Users/djm/claude-projects/edgeless-stack/memory
    python3 -m industry_memory.demo_chroma
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, "/Users/djm/claude-projects/edgeless-stack/memory")

from industry_memory.taxonomy import (
    Contact,
    Address,
    LeadStage,
    JobStatus,
    Priority,
    LocalServiceTaxonomy,
    EntityType,
    Lead,
    Job,
    Vendor,
    Material,
)
from industry_memory.schema import ClientMemorySchema, CollectionBuilder
from industry_memory.client_isolation import ClientIsolationManager
from industry_memory.ingestion import TranscriptIngestionPipeline
from industry_memory.compression import DomainAwareCompressor


def _flatten_metadata(meta: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested dicts for ChromaDB metadata (Chroma only accepts scalar values)."""
    flat: Dict[str, Any] = {}
    for key, value in meta.items():
        full_key = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten_metadata(value, prefix=f"{full_key}_"))
        elif isinstance(value, list):
            flat[full_key] = json.dumps(value)
        else:
            flat[full_key] = value
    return flat


def run_demo():
    print("=" * 60)
    print("LOCAL SERVICE MEMORY KERNEL — CHROMADB DEMO")
    print("Client: Murray Roofing & Remodeling")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Connect to ChromaDB
    # ------------------------------------------------------------------
    print("\n[1] CHROMADB CONNECTION")
    try:
        import chromadb
        client = chromadb.HttpClient(host="localhost", port=8100)
        print(f"  Connected to ChromaDB at localhost:8100")
        print(f"  Version: {client.get_version()}")
    except Exception as e:
        print(f"  ERROR: Cannot connect to ChromaDB: {e}")
        print("  Ensure ChromaDB is running: chroma run --path /path/to/db")
        return

    # ------------------------------------------------------------------
    # 2. Register client with tenant isolation
    # ------------------------------------------------------------------
    print("\n[2] CLIENT REGISTRATION")
    isolation = ClientIsolationManager(chroma_client=client)
    schema = isolation.register_client("Murray Roofing")
    print(f"  Client slug: {schema.client_slug}")
    print(f"  Collections: {schema.get_collection_names()}")

    # ------------------------------------------------------------------
    # 3. Ingestion pipeline
    # ------------------------------------------------------------------
    print("\n[3] TRANSCRIPT INGESTION")
    pipeline = TranscriptIngestionPipeline(client_slug=schema.client_slug)
    compressor = DomainAwareCompressor(max_narrative_chars=300)

    # SMS lead
    sms_text = (
        "Hi this is Mike from 7820 Oakridge Dr, Springfield IL 62704. "
        "We had bad hail last night and I think our roof is damaged. "
        "Can someone come out ASAP? My number is 555-234-5678. "
        "Email: mike.rodriguez@email.com"
    )
    lead_sms = pipeline.ingest_sms(text=sms_text, phone="+155****5678")
    if lead_sms:
        print(f"  SMS lead: {lead_sms.id} | {lead_sms.contact.name} | {lead_sms.project_type} | {lead_sms.urgency.name}")
        # Store in ChromaDB
        doc_text = f"Lead: {lead_sms.contact.name}. {lead_sms.project_type} at {lead_sms.address.street}. {lead_sms.notes}"
        doc_id = isolation.ingest_entity(
            client_slug=schema.client_slug,
            entity_id=lead_sms.id,
            entity_type="lead",
            text=doc_text,
            metadata=_flatten_metadata(lead_sms.to_dict()),
            collection_key="entities",
        )
        print(f"    Stored in ChromaDB: {doc_id}")

    # Email lead
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
    lead_email = pipeline.ingest_email(
        subject="Estimate request for siding replacement",
        body=email_body,
        from_email="jwalsh.home@email.com",
    )
    if lead_email:
        print(f"  Email lead: {lead_email.id} | {lead_email.contact.name} | {lead_email.project_type}")
        doc_text = f"Lead: {lead_email.contact.name}. {lead_email.project_type} at {lead_email.address.street}. {lead_email.notes}"
        doc_id = isolation.ingest_entity(
            client_slug=schema.client_slug,
            entity_id=lead_email.id,
            entity_type="lead",
            text=doc_text,
            metadata=_flatten_metadata(lead_email.to_dict()),
            collection_key="entities",
        )
        print(f"    Stored in ChromaDB: {doc_id}")

    # Call lead
    call_transcript = (
        "Agent: Thanks for calling Murray Roofing. How can I help?\n"
        "Caller: Hi, this is David. We have an active leak in our kitchen ceiling. "
        "Address is 1200 Forest Hills Rd, Springfield IL 62704. "
        "Can you send someone today? It's an emergency.\n"
        "Agent: Absolutely, let me get your info."
    )
    lead_call = pipeline.ingest_call_transcript(
        transcript=call_transcript,
        caller_number="+15555558901",
    )
    if lead_call:
        print(f"  Call lead: {lead_call.id} | {lead_call.contact.name} | {lead_call.urgency.name}")
        doc_text = f"Lead: {lead_call.contact.name}. Emergency {lead_call.project_type} at {lead_call.address.street}. {lead_call.notes}"
        doc_id = isolation.ingest_entity(
            client_slug=schema.client_slug,
            entity_id=lead_call.id,
            entity_type="lead",
            text=doc_text,
            metadata=_flatten_metadata(lead_call.to_dict()),
            collection_key="entities",
        )
        print(f"    Stored in ChromaDB: {doc_id}")

    # ------------------------------------------------------------------
    # 4. Store timeline events
    # ------------------------------------------------------------------
    print("\n[4] TIMELINE EVENTS")
    timeline_spec = schema.get_spec("timeline")
    if timeline_spec:
        timeline_collection = client.get_collection(timeline_spec.name)
        now = datetime.now()
        events = [
            {
                "ts": now.isoformat(),
                "event_type": "lead_created",
                "lead_id": lead_sms.id,
                "channel": "sms",
            },
            {
                "ts": now.isoformat(),
                "event_type": "lead_created",
                "lead_id": lead_email.id,
                "channel": "email",
            },
            {
                "ts": now.isoformat(),
                "event_type": "lead_created",
                "lead_id": lead_call.id,
                "channel": "phone",
            },
        ]
        for i, ev in enumerate(events):
            timeline_collection.add(
                ids=[f"{schema.client_slug}_event_{i}"],
                documents=[json.dumps(ev)],
                metadatas=ev,
            )
        print(f"  Stored {len(events)} events in timeline")

    # ------------------------------------------------------------------
    # 5. Store materials
    # ------------------------------------------------------------------
    print("\n[5] MATERIALS CATALOG")
    materials_spec = schema.get_spec("materials")
    if materials_spec:
        materials_collection = client.get_collection(materials_spec.name)
        materials = [
            {"sku": "SHG-30AR", "description": "Architectural shingles, 30-year", "vendor_id": "vendor_001", "unit_cost": 89.50, "quantity_on_hand": 120},
            {"sku": "SDG-VNL", "description": "Vinyl siding, standard", "vendor_id": "vendor_002", "unit_cost": 45.00, "quantity_on_hand": 80},
            {"sku": "GUT-5K", "description": "5-inch K-style gutter, white", "vendor_id": "vendor_003", "unit_cost": 12.75, "quantity_on_hand": 200},
        ]
        for i, mat in enumerate(materials):
            materials_collection.add(
                ids=[f"{schema.client_slug}_mat_{i}"],
                documents=[f"{mat['sku']}: {mat['description']} — ${mat['unit_cost']} | QOH: {mat['quantity_on_hand']}"],
                metadatas={"client_slug": schema.client_slug, **mat},
            )
        print(f"  Stored {len(materials)} materials in catalog")

    # ------------------------------------------------------------------
    # 6. Semantic search
    # ------------------------------------------------------------------
    print("\n[6] SEMANTIC SEARCH")
    results = isolation.search_client(
        client_slug=schema.client_slug,
        query="hail damage roof emergency",
        collection_key="entities",
        limit=5,
    )
    print(f"  Query: 'hail damage roof emergency'")
    print(f"  Results: {len(results)}")
    for r in results:
        meta = r["metadata"]
        print(f"    - {meta.get('entity_type', '?')} | {meta.get('contact', {}).get('name', 'Unknown')} | dist={r['distance']:.4f}")

    # ------------------------------------------------------------------
    # 7. Timeline replay
    # ------------------------------------------------------------------
    print("\n[7] TIMELINE REPLAY")
    timeline_items = isolation.timeline_query(
        client_slug=schema.client_slug,
        limit=10,
    )
    print(f"  Events: {len(timeline_items)}")
    for item in timeline_items:
        meta = item["metadata"]
        print(f"    {meta.get('ts', '?')[:19]} | {meta.get('event_type', '?')} | {meta.get('channel', '?')}")

    # ------------------------------------------------------------------
    # 8. Compression demo on stored entity
    # ------------------------------------------------------------------
    print("\n[8] DOMAIN-AWARE COMPRESSION")
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
    # 9. Vendor and job creation
    # ------------------------------------------------------------------
    print("\n[9] VENDOR + JOB WORKFLOW")
    vendor = Vendor(
        id="vendor_001",
        type=EntityType.VENDOR,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        source_channel="agent_input",
        name="Midwest Supply Co",
        specialty="shingles",
        rating=4.8,
        preferred=True,
    )
    print(f"  Vendor: {vendor.name} ({vendor.specialty}) | Rating: {vendor.rating}")

    job = LocalServiceTaxonomy.create_job_from_estimate(
        job_id="job_001",
        estimate_id="est_001",
        lead_id=lead_sms.id,
        crew_assigned="Crew A",
    )
    LocalServiceTaxonomy.job_status_transition(job, JobStatus.IN_PROGRESS)
    print(f"  Job: {job.id} | Status: {job.status.name} | Crew: {job.crew_assigned}")
    print(f"    Tags: {job.tags}")

    # ------------------------------------------------------------------
    # 10. Cleanup
    # ------------------------------------------------------------------
    print("\n[10] CLEANUP")
    builder = CollectionBuilder(client)
    drop_status = builder.drop_client(schema)
    for name, status in drop_status.items():
        print(f"  {name}: {status}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE — All collections cleaned up")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
