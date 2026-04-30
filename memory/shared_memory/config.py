"""Configuration helpers for the shared memory subsystem."""

from __future__ import annotations

import os
from pathlib import Path


# CUSTOMIZE: Set SHARED_MEMORY_DB_PATH to your SQLite database location.
# Defaults to ./data/shared_memory/events.sqlite3 relative to this package.
DEFAULT_SHARED_MEMORY_DB_PATH = Path(
    os.environ.get(
        "SHARED_MEMORY_DB_PATH",
        str(Path(__file__).resolve().parent.parent / "data" / "shared_memory" / "events.sqlite3"),
    )
)

# CUSTOMIZE: Set CHROMA_DB_PATH to your ChromaDB persistence directory.
# Only needed if you use the ChromaPromoter for semantic memory.
DEFAULT_CHROMA_DB_PATH = Path(
    os.environ.get(
        "CHROMA_DB_PATH",
        str(Path(__file__).resolve().parent.parent / "data" / "chroma"),
    )
)
