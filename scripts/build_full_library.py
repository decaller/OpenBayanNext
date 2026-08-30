#!/usr/bin/env python3
"""
OpenBayan Next — Full Library Stream Ingestion Pipeline (11.5M Chunks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Streams 96 Parquet partitions from Maktabati/shamela-vectors using
hf_hub_download (150+ MB/s), indexes metadata & text into SQLite
(External Content FTS5 with C-level trigger), and uploads 768-dim
Multilingual-E5 vectors to Qdrant with 1-bit Binary Quantization (BQ).
"""

import os
import sys
import gc
import time
import shutil
import sqlite3
import argparse
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from qdrant_client import QdrantClient
from qdrant_client.http import models

TOTAL_PARTITIONS = 96
REPO_ID = "Maktabati/shamela-vectors"
DEFAULT_DB_PATH = "data/shamela_full.db"
DEFAULT_COLLECTION = "shamela_11m"
DEFAULT_QDRANT_HOST = "localhost"
DEFAULT_QDRANT_PORT = 6333


def setup_sqlite(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA page_size = 8192;")
    conn.execute("PRAGMA cache_size = -256000;")  # 256 MB write cache

    conn.execute("""
    CREATE TABLE IF NOT EXISTS prepared_chunks (
        id TEXT PRIMARY KEY,
        chunk_no INTEGER,
        title TEXT,
        author TEXT,
        death_year INTEGER,
        volume_page TEXT,
        char_start INTEGER,
        char_end INTEGER,
        raw_text TEXT NOT NULL,
        text_norm TEXT,
        source TEXT
    );
    """)

    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS prepared_chunks_fts USING fts5(
        raw_text,
        content='prepared_chunks',
        content_rowid='rowid',
        tokenize = 'unicode61 remove_diacritics 2'
    );
    """)

    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS prepared_chunks_ai AFTER INSERT ON prepared_chunks BEGIN
        INSERT INTO prepared_chunks_fts(rowid, raw_text) VALUES (new.rowid, new.raw_text);
    END;
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_title ON prepared_chunks(title);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_author ON prepared_chunks(author);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_death ON prepared_chunks(death_year);")
    conn.commit()
    return conn


def setup_qdrant(client: QdrantClient, collection_name: str):
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if collection_name not in existing:
        print(f"📦 Creating Qdrant collection '{collection_name}' with Binary Quantization & On-Disk FP32...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=768,
                distance=models.Distance.COSINE,
                on_disk=True  # FP32 vectors written directly to disk
            ),
            hnsw_config=models.HnswConfigDiff(
                m=16,
                ef_construct=100,
                on_disk=True  # HNSW graph edges stored on disk
            ),
            quantization_config=models.BinaryQuantization(
                binary=models.BinaryQuantizationConfig(
                    always_ram=True  # 1-bit quantized vectors held in RAM (1.1 GB)
                )
            ),
            optimizers_config=models.OptimizersConfigDiff(
                default_segment_number=8,
                indexing_threshold=0,  # Disable HNSW indexing during ingestion for max throughput
                flush_interval_sec=30
            )
        )
        print("✓ Qdrant collection initialized.")
    else:
        print(f"✓ Qdrant collection '{collection_name}' already exists.")


def ingest_partition(part_idx: int, conn: sqlite3.Connection, qdrant: QdrantClient, collection_name: str):
    fname = f"shamela-{part_idx:05d}.parquet"
    hf_token = os.getenv("HF_TOKEN")

    t0 = time.time()
    print(f"\n[{part_idx+1}/{TOTAL_PARTITIONS}] 📥 Streaming {fname} ...", flush=True)
    
    parquet_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=fname,
        repo_type="dataset",
        token=hf_token
    )

    dl_time = time.time() - t0
    fsize_mb = os.path.getsize(parquet_path) / (1024 * 1024)
    print(f"  ✓ Downloaded {fsize_mb:.1f} MB in {dl_time:.1f}s ({fsize_mb/max(dl_time, 0.1):.1f} MB/s)", flush=True)

    # Read Parquet
    t_read = time.time()
    table = pq.read_table(parquet_path)
    num_rows = table.num_rows

    pylist = table.to_pylist()
    del table

    sqlite_rows = []
    points = []

    for row in pylist:
        chunk_id = str(row["id"])
        chunk_no = int(row.get("chunk_no", 0) or 0)
        title = str(row.get("title", "") or "")
        author = str(row.get("author", "") or "")
        death_year = int(row.get("death_year", 0) or 0)
        volume_page = str(row.get("page", "") or "")
        char_start = int(row.get("char_start", 0) or 0)
        char_end = int(row.get("char_end", 0) or 0)
        raw_text = str(row.get("text", "") or "")
        text_norm = str(row.get("text_norm", "") or "")
        source = str(row.get("source", "shamela") or "shamela")

        sqlite_rows.append((
            chunk_id, chunk_no, title, author, death_year,
            volume_page, char_start, char_end, raw_text, text_norm, source
        ))

        # Vector extraction (PointStruct with empty payload)
        vec = row["vector"]
        if hasattr(vec, 'tolist'):
            vec = vec.tolist()

        points.append(models.PointStruct(
            id=chunk_id,
            vector=[float(x) for x in vec],
            payload={}  # Zero payload saves ~25 GB disk!
        ))

    del pylist

    t_db = time.time()
    # Ingest into SQLite (FTS trigger automatically populates prepared_chunks_fts)
    cur = conn.cursor()
    cur.executemany(
        """INSERT OR REPLACE INTO prepared_chunks VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        sqlite_rows
    )
    conn.commit()
    db_time = time.time() - t_db

    # Bulk upsert to Qdrant in batches of 1,000
    t_qd = time.time()
    qdrant_batch_size = 1000
    for i in range(0, len(points), qdrant_batch_size):
        batch = points[i : i + qdrant_batch_size]
        qdrant.upsert(
            collection_name=collection_name,
            points=batch,
            wait=False
        )
    qd_time = time.time() - t_qd

    # Delete cached parquet file to keep disk bounded
    try:
        if os.path.exists(parquet_path):
            os.remove(parquet_path)
    except Exception:
        pass

    del sqlite_rows, points
    gc.collect()

    total_time = time.time() - t0
    print(f"  ✓ Indexed {num_rows:,} chunks in {total_time:.1f}s (DB: {db_time:.1f}s, Qdrant: {qd_time:.1f}s) -> {num_rows/total_time:.0f} chunks/s", flush=True)


def finalize(conn: sqlite3.Connection, qdrant: QdrantClient, collection_name: str):
    print("\n=======================================================", flush=True)
    print("🔨 FINALIZING FULL LIBRARY ARTIFACTS...", flush=True)
    print("=======================================================")

    # 1. Trigger Qdrant HNSW Indexing
    print("🚀 Triggering Qdrant HNSW index construction...", flush=True)
    qdrant.update_collection(
        collection_name=collection_name,
        optimizer_config=models.OptimizersConfigDiff(
            indexing_threshold=20000
        )
    )
    print("✓ Qdrant optimizer indexing threshold restored.", flush=True)

    # 2. Finalize SQLite
    print("🧹 Compacting & optimizing SQLite database...", flush=True)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    conn.execute("PRAGMA journal_mode = DELETE;")
    conn.execute("PRAGMA optimize;")
    conn.execute("VACUUM;")
    conn.close()
    print("✓ SQLite compacted and finalized.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Full 11.5M Shamela Library Stream Ingestion")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Output SQLite database path")
    parser.add_argument("--qdrant-host", default=DEFAULT_QDRANT_HOST, help="Qdrant host")
    parser.add_argument("--qdrant-port", type=int, default=DEFAULT_QDRANT_PORT, help="Qdrant port")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Qdrant collection name")
    parser.add_argument("--start-partition", type=int, default=0, help="Starting partition index (0-95)")
    parser.add_argument("--limit-partitions", type=int, default=None, help="Limit number of partitions to ingest")
    args = parser.parse_args()

    print("=======================================================", flush=True)
    print("🚀 OPENBAYAN NEXT: 11.5M FULL LIBRARY INGESTION")
    print(f"Database:   {args.db_path}", flush=True)
    print(f"Qdrant:     http://{args.qdrant_host}:{args.qdrant_port}/{args.collection}", flush=True)
    print(f"Partitions: {args.start_partition} to {TOTAL_PARTITIONS - 1}", flush=True)
    print("=======================================================")

    conn = setup_sqlite(args.db_path)
    qdrant = QdrantClient(host=args.qdrant_host, port=args.qdrant_port, timeout=300, check_compatibility=False)
    setup_qdrant(qdrant, args.collection)

    end_part = TOTAL_PARTITIONS
    if args.limit_partitions is not None:
        end_part = min(TOTAL_PARTITIONS, args.start_partition + args.limit_partitions)

    for part_idx in range(args.start_partition, end_part):
        ingest_partition(part_idx, conn, qdrant, args.collection)

    finalize(conn, qdrant, args.collection)
    print("\n🎉 ALL PARTITIONS INGESTED AND INDEXED SUCCESSFULLY!", flush=True)


if __name__ == "__main__":
    main()
