"""Adapters for plugging external search backends into SharedMemoryService.

The original codebase wired these to a specific session initializer. This
cleaned-up version provides a generic ChromaDB adapter and a template for
writing your own.

CUSTOMIZE: Implement your own search adapter functions that match the
signature ``(SearchMemoryRequest) -> Iterable[dict[str, Any]]`` and pass
them to SharedMemoryService as ``semantic_search`` or ``curated_search``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

from .config import DEFAULT_CHROMA_DB_PATH
from .models import SearchMemoryRequest


def build_chromadb_search_adapter(
    chroma_path: str | Path = DEFAULT_CHROMA_DB_PATH,
    collection_name: str = "unified_knowledge",
) -> Callable[[SearchMemoryRequest], Iterable[dict[str, Any]]]:
    """Return a search adapter that queries a ChromaDB collection.

    CUSTOMIZE: Adjust collection_name to match your promotion target.
    """

    def search_adapter(request: SearchMemoryRequest) -> Iterable[dict[str, Any]]:
        try:
            import chromadb
        except ImportError:
            return []

        client = chromadb.PersistentClient(path=str(chroma_path))
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            return []

        where_filter: dict[str, Any] = {}
        if request.agent:
            where_filter["agent"] = request.agent
        if request.project:
            where_filter["project"] = request.project

        results = collection.query(
            query_texts=[request.query],
            n_results=request.limit,
            where=where_filter if where_filter else None,
        )

        normalized: list[dict[str, Any]] = []
        if results and results.get("documents"):
            documents = results["documents"][0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]

            for i, doc in enumerate(documents):
                meta = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0
                # ChromaDB returns distances; convert to similarity score
                score = max(0.0, 1.0 - distance)
                normalized.append(
                    {
                        "score": score,
                        "content": doc,
                        "record_id": ids[i] if i < len(ids) else None,
                        "agent": meta.get("agent"),
                        "project": meta.get("project"),
                        "session_id": meta.get("session_id"),
                        "memory_type": meta.get("memory_type"),
                        "created_at": meta.get("created_at"),
                        "metadata": meta,
                    }
                )
        return normalized

    return search_adapter
