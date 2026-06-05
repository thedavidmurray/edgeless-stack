"""
Client Isolation Manager

Ensures one client's data never bleeds into another.
Provides tenant-scoped CRUD and query interfaces.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from .schema import ClientMemorySchema


class ClientIsolationManager:
    """
    Tenant-scoped memory manager.

    Every write is prefixed with the client slug.
    Every read is filtered to the client's collections.
    """

    def __init__(self, chroma_client, sqlite_conn=None):
        self.chroma = chroma_client
        self.sqlite = sqlite_conn
        self._schemas: Dict[str, ClientMemorySchema] = {}

    def register_client(self, client_name: str) -> ClientMemorySchema:
        """Register a new client and create their collections."""
        schema = ClientMemorySchema(client_name)
        self._schemas[schema.client_slug] = schema

        # Ensure ChromaDB collections exist
        from .schema import CollectionBuilder
        builder = CollectionBuilder(self.chroma)
        builder.ensure_collections(schema)

        # SQLite tenant table (if available)
        if self.sqlite:
            self._ensure_sqlite_tenant(schema.client_slug, client_name)

        return schema

    def _ensure_sqlite_tenant(self, slug: str, original_name: str) -> None:
        """Create per-client SQLite partition."""
        cursor = self.sqlite.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS industry_clients (
                slug TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                active INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO industry_clients (slug, name, created_at)
            VALUES (?, ?, ?)
        """, (slug, original_name, datetime.now().isoformat()))
        self.sqlite.commit()

    def get_schema(self, client_slug: str) -> Optional[ClientMemorySchema]:
        return self._schemas.get(client_slug)

    def ingest_entity(
        self,
        client_slug: str,
        entity_id: str,
        entity_type: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_key: str = "entities",
    ) -> str:
        """
        Ingest an entity document into the client's collection.

        Returns the ChromaDB document ID.
        """
        schema = self.get_schema(client_slug)
        if not schema:
            raise ValueError(f"Client {client_slug} not registered")

        spec = schema.get_spec(collection_key)
        if not spec:
            raise ValueError(f"Collection {collection_key} not defined for client {client_slug}")

        collection = self.chroma.get_collection(spec.name)
        doc_id = f"{client_slug}_{entity_type}_{entity_id}"

        meta = {
            "client_slug": client_slug,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "ingested_at": datetime.now().isoformat(),
            **(metadata or {}),
        }

        collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[meta],
        )
        return doc_id

    def search_client(
        self,
        client_slug: str,
        query: str,
        collection_key: str = "entities",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Semantic search scoped to a single client."""
        schema = self.get_schema(client_slug)
        if not schema:
            raise ValueError(f"Client {client_slug} not registered")

        spec = schema.get_spec(collection_key)
        if not spec:
            return []

        collection = self.chroma.get_collection(spec.name)
        where = {"client_slug": client_slug}
        if filters:
            where.update(filters)

        results = collection.query(
            query_texts=[query],
            n_results=limit,
            where=where,
        )

        # Flatten ChromaDB result structure
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
        return output

    def timeline_query(
        self,
        client_slug: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        event_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Chronological replay of client events."""
        schema = self.get_schema(client_slug)
        if not schema:
            return []

        spec = schema.get_spec("timeline")
        if not spec:
            return []

        collection = self.chroma.get_collection(spec.name)
        where: Dict[str, Any] = {"client_slug": client_slug}
        if event_type:
            where["event_type"] = event_type
        if start:
            where["ts"] = {"$gte": start.isoformat()}
        if end:
            where.setdefault("ts", {})
            where["ts"]["$lte"] = end.isoformat()

        results = collection.get(
            where=where,
            limit=limit,
            include=["metadatas", "documents"],
        )

        items = []
        for i in range(len(results["ids"])):
            items.append({
                "id": results["ids"][i],
                "document": results["documents"][i] if results.get("documents") else "",
                "metadata": results["metadatas"][i] if results.get("metadatas") else {},
            })
        # Sort by timestamp ascending
        items.sort(key=lambda x: x["metadata"].get("ts", ""))
        return items

    def list_clients(self) -> List[str]:
        """Return all registered client slugs."""
        return list(self._schemas.keys())
