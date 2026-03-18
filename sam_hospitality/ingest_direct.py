#!/usr/bin/env python3
"""
Direct ingestion script: bypasses SAM scanner and writes .md, .csv and .json
files directly into Qdrant using the same payload format that SAM expects.

Usage:
  /home/marina/workshopSolace/agentic_ai_PoC_prj_hospitality/.venv-sam/bin/python3 ingest_direct.py
"""

import csv
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

# ── Configuration ────────────────────────────────────────────────────────────

HOTELS_DIR = (
    "/home/marina/workshopSolace/agentic_ai_PoC_prj_hospitality"
    "/bookings-db/output_files/hotels"
)
COLLECTION_NAME  = "hospitality-rag"
QDRANT_URL       = "http://localhost:6333"
EMBEDDING_DIM    = 1536
EMBEDDING_MODEL  = "text-embedding-3-small"
OPENAI_API_KEY   = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE  = os.environ.get("OPENAI_API_ENDPOINT", "https://api.openai.com/v1")
BATCH_SIZE       = 32

# Max file size in KB — skip hotel_bookings.md (~13 MB) and .xlsx
MAX_FILE_KB = 1100

SKIP_FILES  = {"hotel_bookings.md", "hotels.xlsx"}
INCLUDE_EXT = {".md", ".csv", ".json"}

# Markdown splitter settings (matches SAM YAML config)
MD_CHUNK_SIZE    = 600
MD_CHUNK_OVERLAP = 0

# ── Markdown splitter ─────────────────────────────────────────────────────────

def split_markdown(text: str, chunk_size: int = MD_CHUNK_SIZE) -> List[str]:
    """
    Split markdown by headers (#, ##, ###, …).
    Each header + its body becomes a section; sections longer than
    chunk_size are further split by paragraph, then by characters.
    """
    # Split into sections at every header line
    header_re = re.compile(r"^(#{1,6} .+)$", re.MULTILINE)
    positions = [m.start() for m in header_re.finditer(text)]

    sections: List[str] = []
    if positions:
        for i, pos in enumerate(positions):
            end = positions[i + 1] if i + 1 < len(positions) else len(text)
            sections.append(text[pos:end].strip())
        # Text before the first header
        if positions[0] > 0:
            sections.insert(0, text[: positions[0]].strip())
    else:
        sections = [text.strip()]

    chunks: List[str] = []
    for section in sections:
        if not section:
            continue
        if len(section) <= chunk_size:
            chunks.append(section)
        else:
            # Further split by paragraph
            paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 <= chunk_size:
                    current = (current + "\n\n" + para).strip()
                else:
                    if current:
                        chunks.append(current)
                    # If a single paragraph exceeds chunk_size, split by chars
                    if len(para) > chunk_size:
                        for i in range(0, len(para), chunk_size):
                            chunks.append(para[i : i + chunk_size])
                    else:
                        current = para
            if current:
                chunks.append(current)

    return [c for c in chunks if c.strip()]


# ── CSV splitter ──────────────────────────────────────────────────────────────

def split_csv(file_path: str, rows_per_chunk: int = 10) -> List[str]:
    """
    Read a CSV file and convert groups of rows into text chunks.
    Each chunk is a block of 'field: value' lines prefixed with a row separator.
    Tries comma delimiter first, falls back to semicolon / tab.
    """
    chunks: List[str] = []
    rows = []
    for delim in [",", ";", "\t"]:
        try:
            with open(file_path, newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f, delimiter=delim)
                rows = list(reader)
            if rows and len(rows[0]) > 1:   # more than 1 column → correct delimiter
                break
        except Exception as e:
            print(f"  [WARN] CSV read with delimiter={repr(delim)} failed: {e}")
            rows = []

    if not rows:
        print(f"  [ERROR] Cannot parse CSV {file_path}")
        return []

    current_lines: List[str] = []
    current_count = 0

    for row in rows:
        entry = "---\n" + "\n".join(f"{k}: {v}" for k, v in row.items() if v)
        current_lines.append(entry)
        current_count += 1
        if current_count >= rows_per_chunk:
            chunks.append("\n".join(current_lines))
            current_lines = []
            current_count = 0

    if current_lines:
        chunks.append("\n".join(current_lines))

    return chunks


# ── JSON splitter ────────────────────────────────────────────────────────────

def split_json(file_path: str) -> List[str]:
    """
    Parse hotels.json. Supports both a list of hotels and
    a dict with a top-level key (e.g. {"Hotels": [...]}).
    One text chunk per hotel.
    """
    chunks: List[str] = []
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [ERROR] Cannot read JSON {file_path}: {e}")
        return []

    # Unwrap {"Hotels": [...]} or any single-key dict whose value is a list
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                data = v
                break

    if isinstance(data, list):
        for item in data:
            chunks.append(json.dumps(item, ensure_ascii=False, indent=2))
    else:
        chunks.append(json.dumps(data, ensure_ascii=False, indent=2))

    return chunks


# ── File → chunks dispatcher ─────────────────────────────────────────────────

def file_to_chunks(file_path: str) -> Tuple[List[str], str]:
    """Return (list_of_chunks, file_type)."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".md":
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        return split_markdown(text), "markdown"

    elif ext == ".csv":
        return split_csv(file_path), "csv"

    elif ext == ".json":
        return split_json(file_path), "json"

    return [], "unknown"


# ── Embedding ────────────────────────────────────────────────────────────────

def embed_batch(texts: List[str], client) -> List[List[float]]:
    """Call OpenAI embeddings API for a batch of texts."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


# ── Qdrant upsert ─────────────────────────────────────────────────────────────

def upsert_to_qdrant(qdrant_client, points):
    from qdrant_client.http import models
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )


def ensure_collection(qdrant_client):
    from qdrant_client.http import models
    collections = [c.name for c in qdrant_client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        print(f"Creating collection '{COLLECTION_NAME}'...")
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE,
            ),
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)

    # Import clients
    from openai import OpenAI
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models

    openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
    qdrant_client = QdrantClient(url=QDRANT_URL)

    ensure_collection(qdrant_client)

    # ── Collect files to process ─────────────────────────────────────
    files = []
    for fname in sorted(os.listdir(HOTELS_DIR)):
        if fname in SKIP_FILES:
            print(f"  Skipping (blocklist): {fname}")
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in INCLUDE_EXT:
            continue
        fpath = os.path.join(HOTELS_DIR, fname)
        size_kb = os.path.getsize(fpath) / 1024
        if size_kb > MAX_FILE_KB:
            print(f"  Skipping (too large {size_kb:.0f}KB): {fname}")
            continue
        files.append(fpath)

    print(f"\nFiles to ingest: {len(files)}")
    for f in files:
        size_kb = os.path.getsize(f) / 1024
        print(f"  {os.path.basename(f):40s} {size_kb:6.0f} KB")

    total_chunks = 0
    total_upserted = 0

    for file_path in files:
        fname = os.path.basename(file_path)
        size_kb = os.path.getsize(file_path) / 1024
        print(f"\n{'─'*60}")
        print(f"Processing: {fname} ({size_kb:.0f} KB)")

        chunks, file_type = file_to_chunks(file_path)
        if not chunks:
            print(f"  No chunks generated, skipping.")
            continue

        print(f"  Chunks: {len(chunks)}")

        # Build metadata template (same format as SAM scanner)
        now_iso = datetime.now(timezone.utc).isoformat()
        base_meta = {
            "file_path": file_path,
            "file_name": fname,
            "source_type": "localfilesystemdatasource",
            "file_type": file_type,
            "ingestion_timestamp": now_iso,
        }

        # Process in batches of BATCH_SIZE — embed AND upsert per batch
        file_upserted = 0
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_texts = chunks[i : i + BATCH_SIZE]
            batch_end   = min(i + BATCH_SIZE, len(chunks))

            print(f"  [{i+1}–{batch_end}/{len(chunks)}] embed...", end=" ", flush=True)
            try:
                embeddings = embed_batch(batch_texts, openai_client)
            except Exception as e:
                print(f"EMBED ERROR: {e}")
                continue

            points_batch = []
            for text, emb in zip(batch_texts, embeddings):
                payload = {"text": text}
                payload.update(base_meta)
                points_batch.append(
                    qdrant_models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=emb,
                        payload=payload,
                    )
                )

            try:
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points_batch,
                    wait=True,
                )
                file_upserted += len(points_batch)
                print(f"upsert OK", flush=True)
            except Exception as e:
                print(f"UPSERT ERROR: {e}")

        if file_upserted:
            total_chunks   += len(chunks)
            total_upserted += file_upserted
            print(f"  → {file_upserted} points upserted for {fname}")

    # ── Final summary ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Ingestion complete.")
    print(f"  Total chunks processed : {total_chunks}")
    print(f"  Total points in Qdrant : {total_upserted}")

    # Verify
    info = qdrant_client.get_collection(COLLECTION_NAME)
    print(f"  Qdrant collection count: {info.points_count}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
