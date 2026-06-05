#!/usr/bin/env python3
"""
Cron-ready Ingestion Script for Local Service Memory Kernel

Run from crontab every 5 minutes:
    */5 * * * * cd /Users/djm/claude-projects/edgeless-stack/memory && python3 -m industry_memory.cron_ingest --client "Murray Roofing" --drop-dir /var/inbox/murray >> /var/log/murray_ingest.log 2>&1

Supported drop formats:
    - .sms.json  : {"phone": "...", "text": "...", "timestamp": "ISO"}
    - .email.json: {"from": "...", "subject": "...", "body": "...", "timestamp": "ISO"}
    - .call.json : {"transcript": "...", "caller_number": "...", "timestamp": "ISO"}
    - .raw.txt   : plain text (stored as transcript without entity extraction)

Exit codes:
    0 — success (or no files to process)
    1 — connection error (ChromaDB down)
    2 — parse error (malformed input file)
    3 — ingestion error (partial failure)
"""

import argparse
import json
import os
import sys
import glob
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.insert(0, "/Users/djm/claude-projects/edgeless-stack/memory")

from industry_memory.ingestion import TranscriptIngestionPipeline
from industry_memory.client_isolation import ClientIsolationManager
from industry_memory.compression import DomainAwareCompressor


def _flatten_metadata(meta: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested dicts for ChromaDB metadata (Chroma only accepts scalar values)."""
    flat: Dict[str, Any] = {}
    for key, value in meta.items():
        full_key = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten_metadata(value, prefix=f"{full_key}_"))
        elif isinstance(value, list):
            # Store lists as JSON strings
            flat[full_key] = json.dumps(value)
        else:
            flat[full_key] = value
    return flat


class CronIngestionRunner:
    """Batch ingestion runner for cron scheduling."""

    def __init__(self, client_name: str, drop_dir: str, chroma_host: str = "localhost", chroma_port: int = 8100):
        self.client_name = client_name
        self.drop_dir = Path(drop_dir)
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.processed_dir = self.drop_dir / "processed"
        self.error_dir = self.drop_dir / "error"
        self.processed_dir.mkdir(exist_ok=True)
        self.error_dir.mkdir(exist_ok=True)
        self.stats = {"processed": 0, "errors": 0, "leads": 0, "raw": 0}

    def _connect_chroma(self):
        try:
            import chromadb
            return chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
        except Exception as e:
            print(f"ERROR: Cannot connect to ChromaDB at {self.chroma_host}:{self.chroma_port}: {e}", file=sys.stderr)
            sys.exit(1)

    def _load_file(self, path: Path) -> Optional[Dict[str, Any]]:
        suffix = path.suffix.lower()
        if suffix == ".json":
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: JSON parse failed for {path}: {e}", file=sys.stderr)
                return None
        elif suffix == ".txt":
            return {"_raw_text": path.read_text(), "_source": "raw"}
        return None

    def _ingest_file(self, path: Path, isolation: ClientIsolationManager, pipeline: TranscriptIngestionPipeline, compressor: DomainAwareCompressor) -> bool:
        data = self._load_file(path)
        if data is None:
            return False

        schema = isolation.get_schema(pipeline.client_slug)
        if not schema:
            raise ValueError(f"Client not registered: {pipeline.client_slug}")

        try:
            # Route by file extension
            fname = path.name.lower()
            lead = None
            if fname.endswith(".sms.json"):
                lead = pipeline.ingest_sms(
                    text=data.get("text", ""),
                    phone=data.get("phone", "unknown"),
                    timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
                )
            elif fname.endswith(".email.json"):
                lead = pipeline.ingest_email(
                    subject=data.get("subject", ""),
                    body=data.get("body", ""),
                    from_email=data.get("from", "unknown"),
                    timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
                )
            elif fname.endswith(".call.json"):
                lead = pipeline.ingest_call_transcript(
                    transcript=data.get("transcript", ""),
                    caller_number=data.get("caller_number"),
                    timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
                )
            elif fname.endswith(".raw.txt"):
                # Store as raw transcript in timeline
                timeline_spec = schema.get_spec("transcripts")
                if timeline_spec:
                    collection = isolation.chroma.get_collection(timeline_spec.name)
                    doc_id = f"{schema.client_slug}_raw_{hashlib.sha256(data['_raw_text'].encode()).hexdigest()[:12]}"
                    collection.add(
                        ids=[doc_id],
                        documents=[data["_raw_text"]],
                        metadatas={
                            "client_slug": schema.client_slug,
                            "source": "raw_drop",
                            "filename": path.name,
                            "ingested_at": datetime.now().isoformat(),
                        },
                    )
                self.stats["raw"] += 1
                return True

            if lead:
                # Store compressed entity
                compressed_meta = compressor.compress_entity(lead.to_dict())
                doc_text = f"Lead: {lead.contact.name}. {lead.project_type} at {lead.address.street if lead.address else 'unknown'}. {lead.notes}"
                isolation.ingest_entity(
                    client_slug=schema.client_slug,
                    entity_id=lead.id,
                    entity_type="lead",
                    text=doc_text,
                    metadata=_flatten_metadata(compressed_meta),
                    collection_key="entities",
                )
                self.stats["leads"] += 1

            return True
        except Exception as e:
            print(f"ERROR: Ingestion failed for {path}: {e}", file=sys.stderr)
            return False

    def run(self):
        if not self.drop_dir.exists():
            print(f"ERROR: Drop directory does not exist: {self.drop_dir}", file=sys.stderr)
            sys.exit(2)

        chroma = self._connect_chroma()
        isolation = ClientIsolationManager(chroma_client=chroma)
        schema = isolation.register_client(self.client_name)
        pipeline = TranscriptIngestionPipeline(client_slug=schema.client_slug)
        compressor = DomainAwareCompressor(max_narrative_chars=400)

        # Find all ingestible files
        patterns = ["*.sms.json", "*.email.json", "*.call.json", "*.raw.txt"]
        files = []
        for pat in patterns:
            files.extend(self.drop_dir.glob(pat))

        if not files:
            print(f"No files to process in {self.drop_dir}")
            sys.exit(0)

        for path in sorted(files):
            success = self._ingest_file(path, isolation, pipeline, compressor)
            if success:
                dest = self.processed_dir / path.name
                path.rename(dest)
                self.stats["processed"] += 1
            else:
                dest = self.error_dir / path.name
                path.rename(dest)
                self.stats["errors"] += 1

        # Write ingestion log
        log_path = self.processed_dir / f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_path, "w") as f:
            json.dump({
                "ts": datetime.now().isoformat(),
                "client": self.client_name,
                "client_slug": schema.client_slug,
                "stats": self.stats,
            }, f, indent=2)

        print(f"Ingestion complete: {self.stats['processed']} processed, {self.stats['leads']} leads, {self.stats['raw']} raw, {self.stats['errors']} errors")
        if self.stats["errors"] > 0:
            sys.exit(3)


def main():
    parser = argparse.ArgumentParser(description="Cron ingestion for local service memory kernel")
    parser.add_argument("--client", required=True, help="Client business name")
    parser.add_argument("--drop-dir", required=True, help="Directory to watch for incoming files")
    parser.add_argument("--chroma-host", default="localhost", help="ChromaDB host")
    parser.add_argument("--chroma-port", type=int, default=8100, help="ChromaDB port")
    args = parser.parse_args()

    runner = CronIngestionRunner(
        client_name=args.client,
        drop_dir=args.drop_dir,
        chroma_host=args.chroma_host,
        chroma_port=args.chroma_port,
    )
    runner.run()


if __name__ == "__main__":
    main()
