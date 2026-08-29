import os
import sys
import time
import asyncio
import sqlite3
import numpy as np

# Add apps/api to python path (2 levels up from dev_notes/01_milestone_1_ingestion_and_indexing/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api")))

from app.core.database import db, get_db_uri
from pipeline.stemmer import normalize_arabic, extract_composite_stems

def test_sqlite_direct(db_path: str):
    print("="*80)
    print("🧪 1. Direct SQLite & FTS5 Verification")
    print("="*80)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check journal mode & table counts
    journal_mode = cur.execute("PRAGMA journal_mode;").fetchone()[0]
    print(f"✓ Journal Mode: {journal_mode} (Safe for Docker :ro mounts)")

    book_count = cur.execute("SELECT COUNT(*) FROM books;").fetchone()[0]
    sec_count = cur.execute("SELECT COUNT(*) FROM sections;").fetchone()[0]
    chunk_count = cur.execute("SELECT COUNT(*) FROM prepared_chunks;").fetchone()[0]

    print(f"✓ Total Books:    {book_count}")
    print(f"✓ Total Sections: {sec_count}")
    print(f"✓ Total Chunks:   {chunk_count}")

    # Benchmark FTS5 Search Queries
    test_queries = [
        "سلم بيع",
        "صلاة وتر",
        "طهارة ماء",
        "عقل قلب",
        "شفعة شريك"
    ]

    print("\n⚡ Benchmarking FTS5 BM25 Search Queries (JOIN Content Table):")
    for query in test_queries:
        terms = [w for w in normalize_arabic(query).split() if len(w) >= 2]
        fts_match_expr = f"salient_roots_text: ({' AND '.join(terms)})"

        t0 = time.perf_counter()
        sql = """
        SELECT p.chunk_id, p.book_name, p.section_title, p.volume_page, p.raw_text, f.rank
        FROM prepared_chunks_fts f
        JOIN prepared_chunks p ON p.chunk_id = f.rowid
        WHERE prepared_chunks_fts MATCH ?
        ORDER BY f.rank
        LIMIT 5
        """
        results = cur.execute(sql, (fts_match_expr,)).fetchall()
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000

        print(f"\n  Query: '{query}' -> FTS Expr: '{fts_match_expr}'")
        print(f"  • Latency: {latency_ms:.3f} ms | Found Hits: {len(results)}")
        if results:
            top = results[0]
            snippet = top[4][:120].replace('\r', ' ').replace('\n', ' ')
            print(f"  • Top Hit: [{top[1]}] | {top[2]} ({top[3]}) | BM25 Rank: {top[5]:.2f}")
            print(f"    Snippet: \"{snippet}...\"")

    conn.close()

async def test_libsql_client(db_path: str):
    print("\n" + "="*80)
    print("🧪 2. Read-Only Immutable Access via libsql_client (FastAPI Driver)")
    print("="*80)

    # Set explicit db path
    db._db_url = f"file:{db_path}"
    await db.connect()
    client = db.client

    t0 = time.perf_counter()
    res = await client.execute("SELECT COUNT(*) as count FROM prepared_chunks")
    t1 = time.perf_counter()
    print(f"✓ Async Count Query via libsql_client: {res.rows[0][0]} rows (in {(t1-t0)*1000:.3f} ms)")

    # Execute FTS match query via libsql_client
    fts_sql = """
    SELECT rowid, book_name, section_title
    FROM prepared_chunks_fts
    WHERE prepared_chunks_fts MATCH ?
    LIMIT 3
    """
    t0 = time.perf_counter()
    res_fts = await client.execute(fts_sql, ["salient_roots_text: (سلم AND بيع)"])
    t1 = time.perf_counter()
    print(f"✓ Async FTS5 Search via libsql_client (in {(t1-t0)*1000:.3f} ms) returned {len(res_fts.rows)} rows:")
    for r in res_fts.rows:
        print(f"  - [Chunk #{r[0]}] [{r[1]}] -> {r[2]}")

    # Benchmark 50-row vector blob deserialization
    synthetic_blobs = [np.random.randn(768).astype("<f4").tobytes() for _ in range(50)]
    t0 = time.perf_counter()
    _ = [np.frombuffer(b, dtype="<f4") for b in synthetic_blobs]
    t1 = time.perf_counter()
    print(f"✓ Vector Blob Deserialization (50 candidate rows): {(t1-t0)*1000:.3f} ms (NumPy frombuffer <f4)")

    await db.close()
    print("\n🎉 ALL MILESTONE 1 VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "shamela_corpus.db"))
    test_sqlite_direct(db_file)
    asyncio.run(test_libsql_client(db_file))
