# Industry Memory Kernel

Task-centric memory system for local service businesses. First vertical: **roofing/remodeling contractor**.

---

## Quick Start

```bash
cd /Users/djm/claude-projects/edgeless-stack/memory

# 1. Install dependencies
pip install -r requirements.txt
pip install chromadb  # optional, for semantic memory

# 2. Run the demo (no ChromaDB required)
python3 -m industry_memory.demo_contractor

# 3. Run the full demo (requires ChromaDB running)
chroma run --path /path/to/chroma_data  # in another terminal
python3 -m industry_memory.demo_chroma
```

---

## Architecture

```
industry_memory/
├── taxonomy.py          # Domain entities, enums, state machines
├── schema.py             # ChromaDB collection schema per client
├── client_isolation.py   # Tenant-scoped CRUD + search
├── ingestion.py         # SMS/email/call → structured lead extraction
├── compression.py        # Domain-aware compression (lossless/lossy/semantic)
├── demo_contractor.py   # Standalone demo (no DB)
├── demo_chroma.py       # End-to-end demo with ChromaDB
├── cron_ingest.py       # Cron-ready batch ingestion runner
└── verticalization_template.md  # Guide for logistics, legal, medical billing
```

---

## Core Concepts

### 1. Domain Taxonomy

Entity types: `Lead`, `Estimate`, `Job`, `Vendor`, `Material`, `ScheduleBlock`, `Invoice`, `Photo`, `Note`, `CallTranscript`, `SMS_Thread`, `EmailThread`

State machines:
- `LeadStage`: COLD → CONTACTED → ESTIMATE_SCHEDULED → ESTIMATE_SENT → NEGOTIATING → WON / LOST / DORMANT
- `JobStatus`: PENDING_START → MATERIALS_ORDERED → IN_PROGRESS → INSPECTION_PENDING → COMPLETE → INVOICED → PAID / DISPUTE

### 2. Tenant Isolation

Each client gets 4 isolated ChromaDB collections:
- `{slug}_entities` — semantic search over leads, jobs, vendors
- `{slug}_transcripts` — raw SMS/email/call transcripts
- `{slug}_timeline` — time-ordered events for replay
- `{slug}_materials` — material catalog and inventory

Client slug is salted with a hash to prevent PII leakage in collection names.

### 3. Domain-Aware Compression

- **Lossless**: numeric fields, dates, statuses, IDs, vendor ratings, lat/lng
- **Lossy**: customer narrative, call small-talk, email signatures
- **Semantic preserve**: sentences containing state transitions (approved, started, completed, delayed, payment received)

### 4. Ingestion Pipeline

Regex-based extraction (no LLM required for latency):
- Addresses: `123 Main St, City, ST 12345`
- Phones: `555-234-5678`
- Emails: `name@domain.com`
- Urgency: keyword scoring (emergency, asap, hail damage, active leak)
- Project type: keyword scoring (roof_repair, siding, gutters, remodel)

---

## Cron Setup

```bash
# Add to crontab
crontab -e

# Every 5 minutes, ingest files from drop directory
*/5 * * * * cd /Users/djm/claude-projects/edgeless-stack/memory && python3 -m industry_memory.cron_ingest --client "Murray Roofing" --drop-dir /var/inbox/murray >> /var/log/murray_ingest.log 2>&1
```

Drop file formats:
- `.sms.json`: `{"phone": "...", "text": "...", "timestamp": "2026-06-01T10:00:00"}`
- `.email.json`: `{"from": "...", "subject": "...", "body": "...", "timestamp": "..."}`
- `.call.json`: `{"transcript": "...", "caller_number": "...", "timestamp": "..."}`
- `.raw.txt`: plain text (stored as transcript, no entity extraction)

---

## Verticalization

See `verticalization_template.md` for adapting to:
- **Logistics** — delivery fleet, tracking, route optimization
- **Legal** — matters, deadlines, docket numbers, filings
- **Medical Billing** — encounters, CPT/ICD codes, claims, prior auth

The shared infrastructure (schema, isolation, compression base class, cron runner) is vertical-agnostic.

---

## Reference

- Issue: EDGA-4265
- Project: `/Users/djm/claude-projects/products/edgeless-stack/memory/`
- ChromaDB: localhost:8100
