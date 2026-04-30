"""Small FastAPI surface for the shared memory contract.

CUSTOMIZE: Set SHARED_MEMORY_DB_PATH and CHROMA_DB_PATH env vars before
starting. Optionally pass your own search adapters to the service constructor.

Run with:
    uvicorn shared_memory.api:app --host 127.0.0.1 --port 8042
"""

from __future__ import annotations

from fastapi import FastAPI

from .adapters import build_chromadb_search_adapter
from .config import DEFAULT_CHROMA_DB_PATH, DEFAULT_SHARED_MEMORY_DB_PATH
from .models import (
    ContextBundle,
    ContextRequest,
    MemoryPromotionReceipt,
    MemoryPromotionRequest,
    PromotionRunReceipt,
    SearchMemoryRequest,
    SearchMemoryResponse,
    WriteEpisodeReceipt,
    WriteEpisodeRequest,
)
from .service import SharedMemoryService


app = FastAPI(
    title="Shared Memory API",
    description="Cross-runtime shared memory surface for multi-agent systems.",
    version="0.1.0",
)

# CUSTOMIZE: Replace with your own search adapters if not using ChromaDB.
_service: SharedMemoryService | None = None


def _get_service() -> SharedMemoryService:
    global _service
    if _service is None:
        _service = SharedMemoryService.from_sqlite_path(
            DEFAULT_SHARED_MEMORY_DB_PATH,
            semantic_search=build_chromadb_search_adapter(
                chroma_path=DEFAULT_CHROMA_DB_PATH,
            ),
        )
    return _service


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "shared-memory",
        "db_path": str(DEFAULT_SHARED_MEMORY_DB_PATH),
    }


@app.post("/episodes", response_model=WriteEpisodeReceipt)
def write_episode(request: WriteEpisodeRequest) -> WriteEpisodeReceipt:
    return _get_service().write_episode(request)


@app.post("/promotions", response_model=MemoryPromotionReceipt)
def promote_memory(request: MemoryPromotionRequest) -> MemoryPromotionReceipt:
    return _get_service().promote_memory(request)


@app.post("/search", response_model=SearchMemoryResponse)
def search_memory(request: SearchMemoryRequest) -> SearchMemoryResponse:
    return _get_service().search_memory(request)


@app.post("/context", response_model=ContextBundle)
def get_context(request: ContextRequest) -> ContextBundle:
    return _get_service().get_context(request)


@app.post("/promotions/process", response_model=PromotionRunReceipt)
def process_promotions(limit: int = 10) -> PromotionRunReceipt:
    return _get_service().process_promotions(limit=limit)


if __name__ == "__main__":
    import uvicorn

    # CUSTOMIZE: Change host/port as needed.
    uvicorn.run(app, host="127.0.0.1", port=8042)
