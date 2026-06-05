"""
Domain Taxonomy — Local Service Vertical (Roofing/Remodeling Contractor)

Defines the entity types, statuses, and relationships that form the
memory kernel for contractor operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import json


class EntityType(Enum):
    LEAD = auto()
    ESTIMATE = auto()
    JOB = auto()
    VENDOR = auto()
    MATERIAL = auto()
    SCHEDULE_BLOCK = auto()
    INVOICE = auto()
    PHOTO = auto()
    NOTE = auto()
    CALL_TRANSCRIPT = auto()
    SMS_THREAD = auto()
    EMAIL_THREAD = auto()


class LeadStage(Enum):
    COLD = auto()
    CONTACTED = auto()
    ESTIMATE_SCHEDULED = auto()
    ESTIMATE_SENT = auto()
    NEGOTIATING = auto()
    WON = auto()
    LOST = auto()
    DORMANT = auto()


class JobStatus(Enum):
    PENDING_START = auto()
    MATERIALS_ORDERED = auto()
    IN_PROGRESS = auto()
    INSPECTION_PENDING = auto()
    COMPLETE = auto()
    INVOICED = auto()
    PAID = auto()
    DISPUTE = auto()


class EstimateStatus(Enum):
    DRAFT = auto()
    SENT = auto()
    VIEWED = auto()
    APPROVED = auto()
    REJECTED = auto()
    EXPIRED = auto()


class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    EMERGENCY = 5


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    lat: Optional[float] = None
    lng: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "lat": self.lat,
            "lng": self.lng,
        }


@dataclass
class Contact:
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    role: str = "homeowner"  # homeowner, property_manager, adjuster, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "role": self.role,
        }


@dataclass
class Entity:
    """Base entity with common fields for all memory objects."""
    id: str
    type: EntityType
    created_at: datetime
    updated_at: datetime
    source_channel: str  # sms, email, phone, web_form, agent_input
    raw_transcript_ref: Optional[str] = None
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "source_channel": self.source_channel,
            "raw_transcript_ref": self.raw_transcript_ref,
            "confidence": self.confidence,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Lead(Entity):
    contact: Optional[Contact] = None
    address: Optional[Address] = None
    stage: LeadStage = LeadStage.COLD
    project_type: str = ""  # roof_repair, full_replacement, siding, etc.
    notes: str = ""
    estimated_value: Optional[float] = None
    urgency: Priority = Priority.NORMAL

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "contact": self.contact.to_dict() if self.contact else None,
            "address": self.address.to_dict() if self.address else None,
            "stage": self.stage.name,
            "project_type": self.project_type,
            "notes": self.notes,
            "estimated_value": self.estimated_value,
            "urgency": self.urgency.name,
        })
        return base


@dataclass
class Estimate(Entity):
    lead_id: Optional[str] = None
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    total: float = 0.0
    status: EstimateStatus = EstimateStatus.DRAFT
    sent_at: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    materials_list: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "lead_id": self.lead_id,
            "line_items": self.line_items,
            "total": self.total,
            "status": self.status.name,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "materials_list": self.materials_list,
        })
        return base


@dataclass
class Job(Entity):
    estimate_id: Optional[str] = None
    lead_id: Optional[str] = None
    status: JobStatus = JobStatus.PENDING_START
    crew_assigned: Optional[str] = None
    start_date: Optional[datetime] = None
    target_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    materials_status: str = "not_ordered"
    permit_required: bool = False
    permit_status: str = "not_needed"
    inspection_required: bool = False
    inspection_status: str = "not_needed"
    photos: List[str] = field(default_factory=list)
    weather_delays: int = 0

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "estimate_id": self.estimate_id,
            "lead_id": self.lead_id,
            "status": self.status.name,
            "crew_assigned": self.crew_assigned,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_completion": self.target_completion.isoformat() if self.target_completion else None,
            "actual_completion": self.actual_completion.isoformat() if self.actual_completion else None,
            "materials_status": self.materials_status,
            "permit_required": self.permit_required,
            "permit_status": self.permit_status,
            "inspection_required": self.inspection_required,
            "inspection_status": self.inspection_status,
            "photos": self.photos,
            "weather_delays": self.weather_delays,
        })
        return base


@dataclass
class Vendor(Entity):
    name: str = ""
    specialty: str = ""  # shingles, siding, gutters, lumber, etc.
    contact: Optional[Contact] = None
    payment_terms: str = "net_30"
    rating: Optional[float] = None
    last_used: Optional[datetime] = None
    preferred: bool = False

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "name": self.name,
            "specialty": self.specialty,
            "contact": self.contact.to_dict() if self.contact else None,
            "payment_terms": self.payment_terms,
            "rating": self.rating,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "preferred": self.preferred,
        })
        return base


@dataclass
class Material(Entity):
    sku: Optional[str] = None
    description: str = ""
    vendor_id: Optional[str] = None
    unit_cost: Optional[float] = None
    quantity_on_hand: int = 0
    quantity_ordered: int = 0
    reorder_threshold: int = 10
    location: str = "warehouse"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "sku": self.sku,
            "description": self.description,
            "vendor_id": self.vendor_id,
            "unit_cost": self.unit_cost,
            "quantity_on_hand": self.quantity_on_hand,
            "quantity_ordered": self.quantity_ordered,
            "reorder_threshold": self.reorder_threshold,
            "location": self.location,
        })
        return base


class LocalServiceTaxonomy:
    """
    Taxonomy manager for local service verticals.

    Provides entity factory methods, validation, and serialization.
    """

    ENTITY_CLASSES = {
        EntityType.LEAD: Lead,
        EntityType.ESTIMATE: Estimate,
        EntityType.JOB: Job,
        EntityType.VENDOR: Vendor,
        EntityType.MATERIAL: Material,
    }

    @classmethod
    def create_lead(
        cls,
        lead_id: str,
        contact: Contact,
        address: Address,
        project_type: str,
        source_channel: str = "sms",
        urgency: Priority = Priority.NORMAL,
    ) -> Lead:
        now = datetime.now()
        return Lead(
            id=lead_id,
            type=EntityType.LEAD,
            created_at=now,
            updated_at=now,
            source_channel=source_channel,
            contact=contact,
            address=address,
            project_type=project_type,
            urgency=urgency,
            tags=["auto-ingested", project_type],
        )

    @classmethod
    def create_estimate(
        cls,
        estimate_id: str,
        lead_id: str,
        line_items: List[Dict[str, Any]],
        source_channel: str = "agent_input",
    ) -> Estimate:
        now = datetime.now()
        total = sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in line_items)
        materials = list({item.get("material_id") for item in line_items if item.get("material_id")})
        return Estimate(
            id=estimate_id,
            type=EntityType.ESTIMATE,
            created_at=now,
            updated_at=now,
            source_channel=source_channel,
            lead_id=lead_id,
            line_items=line_items,
            total=round(total, 2),
            materials_list=materials,
        )

    @classmethod
    def create_job_from_estimate(
        cls,
        job_id: str,
        estimate_id: str,
        lead_id: str,
        crew_assigned: Optional[str] = None,
        source_channel: str = "agent_input",
    ) -> Job:
        now = datetime.now()
        return Job(
            id=job_id,
            type=EntityType.JOB,
            created_at=now,
            updated_at=now,
            source_channel=source_channel,
            estimate_id=estimate_id,
            lead_id=lead_id,
            crew_assigned=crew_assigned,
            status=JobStatus.PENDING_START,
            tags=["from_estimate", estimate_id],
        )

    @classmethod
    def stage_transition(cls, lead: Lead, new_stage: LeadStage) -> Lead:
        lead.stage = new_stage
        lead.updated_at = datetime.now()
        lead.tags.append(f"stage:{new_stage.name}")
        return lead

    @classmethod
    def job_status_transition(cls, job: Job, new_status: JobStatus) -> Job:
        job.status = new_status
        job.updated_at = datetime.now()
        if new_status == JobStatus.COMPLETE:
            job.actual_completion = datetime.now()
        job.tags.append(f"status:{new_status.name}")
        return job
