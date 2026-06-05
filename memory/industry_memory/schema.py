"""
ChromaDB Collection Schema — Per-client isolated memory collections.

Each client (contractor business) gets their own collection prefix.
Collections are organized by entity type for efficient retrieval.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json


@dataclass
class CollectionSpec:
    """Specification for a ChromaDB collection."""
    name: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding_model: str = "text-embedding-3-small"
    distance_fn: str = "cosine"


class ClientMemorySchema:
    """
    Schema builder for a single client's memory kernel.

    Creates 4 collections per client:
      - {client_slug}_entities     → semantic search over leads, jobs, vendors
      - {client_slug}_transcripts  → raw SMS/email/call transcripts
      - {client_slug}_timeline     → time-ordered events for chronological replay
      - {client_slug}_materials    → material catalog and inventory
    """

    COLLECTIONS = {
        "entities": {
            "description": "Semantic index of leads, estimates, jobs, vendors, and materials",
            "metadata": {"category": "entity", "searchable": True},
        },
        "transcripts": {
            "description": "Raw transcripts from SMS, email, and phone calls",
            "metadata": {"category": "raw", "searchable": True, "compression": "lossy"},
        },
        "timeline": {
            "description": "Time-ordered events for chronological replay and audit",
            "metadata": {"category": "event", "searchable": False, "sort_key": "ts"},
        },
        "materials": {
            "description": "Material catalog, inventory levels, and vendor links",
            "metadata": {"category": "inventory", "searchable": True, "compression": "lossless"},
        },
    }

    def __init__(self, client_slug: str, embedding_model: str = "text-embedding-3-small"):
        self.client_slug = self._sanitize_slug(client_slug)
        self.embedding_model = embedding_model
        self._collections: Dict[str, CollectionSpec] = {}
        self._build_specs()

    @staticmethod
    def _sanitize_slug(name: str) -> str:
        """Create a safe collection name prefix."""
        clean = name.lower().strip().replace(" ", "_").replace("-", "_")
        clean = "".join(c for c in clean if c.isalnum() or c == "_")
        # Add hash to guarantee uniqueness without leaking PII
        suffix = hashlib.sha256(name.encode()).hexdigest()[:8]
        return f"{clean}_{suffix}"

    def _build_specs(self) -> None:
        for key, info in self.COLLECTIONS.items():
            self._collections[key] = CollectionSpec(
                name=f"{self.client_slug}_{key}",
                description=info["description"],
                metadata={
                    **info["metadata"],
                    "client_slug": self.client_slug,
                    "embedding_model": self.embedding_model,
                },
                embedding_model=self.embedding_model,
            )

    def get_collection_names(self) -> List[str]:
        return [spec.name for spec in self._collections.values()]

    def get_spec(self, key: str) -> Optional[CollectionSpec]:
        return self._collections.get(key)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_slug": self.client_slug,
            "embedding_model": self.embedding_model,
            "collections": {
                key: {
                    "name": spec.name,
                    "description": spec.description,
                    "metadata": spec.metadata,
                }
                for key, spec in self._collections.items()
            },
        }


class CollectionBuilder:
    """
    Idempotent collection creator for ChromaDB.

    Usage:
        builder = CollectionBuilder(chroma_client)
        schema = ClientMemorySchema("Murray_Roofing")
        builder.ensure_collections(schema)
    """

    def __init__(self, chroma_client):
        self.client = chroma_client

    def ensure_collections(self, schema: ClientMemorySchema) -> Dict[str, Any]:
        """Create collections if they don't exist; return status map."""
        status = {}
        for key in ClientMemorySchema.COLLECTIONS:
            spec = schema.get_spec(key)
            if not spec:
                status[key] = "missing_spec"
                continue
            try:
                existing = self.client.get_collection(spec.name)
                if existing:
                    status[key] = "exists"
                    continue
            except Exception:
                pass
            try:
                self.client.create_collection(
                    name=spec.name,
                    metadata=spec.metadata,
                )
                status[key] = "created"
            except Exception as e:
                status[key] = f"error:{e}"
        return status

    def drop_client(self, schema: ClientMemorySchema) -> Dict[str, str]:
        """Remove all collections for a client."""
        status = {}
        for name in schema.get_collection_names():
            try:
                self.client.delete_collection(name)
                status[name] = "deleted"
            except Exception as e:
                status[name] = f"error:{e}"
        return status
