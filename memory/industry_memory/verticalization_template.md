# Verticalization Template: Local Service Memory Kernel

This document shows how to adapt the roofing/remodeling contractor kernel to other local service verticals.

---

## 1. Logistics / Delivery Fleet

### Domain Taxonomy Changes

| Entity | Roofing Kernel | Logistics Kernel |
|--------|--------------|------------------|
| Lead | Homeowner inquiry | Shipment request (B2B or B2C) |
| Estimate | Repair/replacement quote | Route + rate quote |
| Job | Roofing project | Delivery run / route |
| Vendor | Material supplier | Carrier / 3PL partner |
| Material | Shingles, siding, gutters | SKU inventory, pallet, container |
| Schedule Block | Crew assignment | Driver + vehicle + time window |

### New Entity Types

```python
class DeliveryStatus(Enum):
    PENDING_PICKUP = auto()
    IN_TRANSIT = auto()
    AT_HUB = auto()
    OUT_FOR_DELIVERY = auto()
    DELIVERED = auto()
    EXCEPTION = auto()
    RETURNED = auto()

class VehicleType(Enum):
    VAN = auto()
    BOX_TRUCK = auto()
    FLATBED = auto()
    REFRIGERATED = auto()

@dataclass
class Shipment(Entity):
    tracking_id: str
    origin: Address
    destination: Address
    weight_kg: float
    dimensions: Dict[str, float]  # l, w, h
    service_level: str  # ground, express, same_day
    signature_required: bool
    delivery_status: DeliveryStatus
    pod_ref: Optional[str] = None  # proof of delivery photo
```

### Ingestion Sources
- EDI 204/214 feeds (carrier status updates)
- Driver mobile app check-ins (SMS / push)
- GPS breadcrumb streams (compressed to hub events)
- Customer portal chat transcripts

### Compression Strategy
- **Lossless**: tracking_id, lat/lng, timestamps, weight, dimensions
- **Lossy**: customer complaint narrative, driver call small-talk
- **Semantic preserve**: delivery_exceptions, access failures, signature events

---

## 2. Legal / Law Firm

### Domain Taxonomy Changes

| Entity | Roofing Kernel | Legal Kernel |
|--------|--------------|--------------|
| Lead | Homeowner inquiry | Intake / consultation request |
| Estimate | Repair quote | Fee estimate / retainer proposal |
| Job | Roofing project | Matter / case |
| Vendor | Material supplier | Expert witness, court reporter, process server |
| Material | Shingles, gutters | Document exhibits, discovery files |
| Schedule Block | Crew assignment | Court date, deposition, filing deadline |

### New Entity Types

```python
class MatterStatus(Enum):
    INTAKE = auto()
    CONFLICTS_CLEARED = auto()
    ENGAGED = auto()
    PENDING_DISCOVERY = auto()
    LITIGATION = auto()
    SETTLEMENT = auto()
    CLOSED = auto()

class FilingDeadline(Entity):
    matter_id: str
    deadline_type: str  # answer, motion, discovery, appeal
    due_date: datetime
    filed_date: Optional[datetime]
    extension_granted: bool
    jurisdiction: str
    court: str
    docket_number: str
```

### Ingestion Sources
- Email (client, opposing counsel, court notices)
- Court e-filing notifications (PACER, state portals)
- Transcription services (depositions, hearings)
- Phone intake calls
- Client portal messages

### Compression Strategy
- **Lossless**: docket numbers, deadlines, dollar amounts, filing dates
- **Lossy**: emotional client narrative, billing discussions
- **Semantic preserve**: settlement offers, deadline changes, conflict waivers

---

## 3. Medical Billing / Practice Management

### Domain Taxonomy Changes

| Entity | Roofing Kernel | Medical Billing Kernel |
|--------|--------------|------------------------|
| Lead | Homeowner inquiry | Patient referral / new appointment request |
| Estimate | Repair quote | Pre-auth / cost estimate / patient responsibility |
| Job | Roofing project | Visit / procedure / claim |
| Vendor | Material supplier | Payer / insurance carrier |
| Material | Shingles, gutters | CPT/HCPCS codes, supplies, medications |
| Schedule Block | Crew assignment | Appointment slot + provider + room |

### New Entity Types

```python
class ClaimStatus(Enum):
    PENDING_AUTH = auto()
    AUTH_APPROVED = auto()
    SUBMITTED = auto()
    PENDING_PAYMENT = auto()
    PAID = auto()
    DENIED = auto()
    APPEALED = auto()
    WRITE_OFF = auto()

class PatientEncounter(Entity):
    patient_id: str
    provider_id: str
    appointment_date: datetime
    cpt_codes: List[str]
    diagnosis_codes: List[str]  # ICD-10
    prior_auth_ref: Optional[str]
    claim_status: ClaimStatus
    billed_amount: float
    allowed_amount: Optional[float]
    paid_amount: Optional[float]
    patient_responsibility: float
    denial_reason: Optional[str]
```

### Ingestion Sources
- EDI 837/835 transactions (claim submission / remittance)
- Eligibility verification API responses (270/271)
- Patient portal messages
- Prior auth fax / portal submissions
- Payer correspondence (EOB, denial letters)

### Compression Strategy
- **Lossless**: CPT/ICD codes, dollar amounts, auth numbers, NPIs, claim IDs
- **Lossy**: patient narrative, clinical notes (already in EHR)
- **Semantic preserve**: denial reasons, appeal deadlines, patient responsibility changes

---

## 4. Verticalization Checklist

For each new vertical:

1. [ ] **Copy taxonomy.py** and rename entity types/stages/statuses
2. [ ] **Define new entity dataclasses** with domain-specific fields
3. [ ] **Update ingestion.py** regex patterns and keyword maps
4. [ ] **Adjust compression.py** PRESERVE_FIELDS and TRANSITION_TRIGGERS
5. [ ] **Schema.py** stays unchanged (4 collections per client are generic)
6. [ ] **Update cron_ingest.py** to handle new file formats if needed
7. [ ] **Write demo_*.py** for the new vertical
8. [ ] **Test with ChromaDB** end-to-end

---

## 5. Shared Infrastructure (No Changes Needed)

The following components are vertical-agnostic:

- `schema.py` — ClientMemorySchema, CollectionBuilder
- `client_isolation.py` — ClientIsolationManager, tenant CRUD
- `compression.py` base class — DomainAwareCompressor (only subclass rules)
- `cron_ingest.py` runner — file routing shell (only parsers change)

---

*Reference: EDGA-4265 | Roofing/Remodeling as canonical vertical*
