"""
Industry Memory Kernel — Task-centric memory for local service verticals.

First vertical: Roofing/Remodeling Contractor
Reference: EDGA-4265
"""

from .taxonomy import LocalServiceTaxonomy, EntityType, JobStatus, LeadStage
from .schema import ClientMemorySchema, CollectionBuilder
from .client_isolation import ClientIsolationManager
from .ingestion import TranscriptIngestionPipeline
from .compression import DomainAwareCompressor

from .demo_chroma import run_demo as run_chroma_demo
from .cron_ingest import CronIngestionRunner

__all__ = [
    "LocalServiceTaxonomy",
    "EntityType",
    "JobStatus",
    "LeadStage",
    "ClientMemorySchema",
    "CollectionBuilder",
    "ClientIsolationManager",
    "TranscriptIngestionPipeline",
    "DomainAwareCompressor",
    "run_chroma_demo",
    "CronIngestionRunner",
]
