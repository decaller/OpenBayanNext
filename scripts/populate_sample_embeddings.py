import os
import sys
import time
import sqlite3
import numpy as np

# Add apps/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "api")))
from app.core.vectorizer import vectorizer

def populate_vectors(db_path: str, limit: int = 10000):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check chunks without embeddings
    empty_count = cur.execute("SELECT COUNT(*) FROM prepared_chunks WHERE embedding IS NULL").fetchone()[0]
    print(f"📊 Chunks needing embeddings: {empty_count}")
    
    if empty_count == 0:
        print("✓ All chunks already have embeddings!")
        conn.close()
        return

    vectorizer.warmup()

    # Process in batches
    batch_size = 500
    cur.execute("SELECT chunk_id, raw_text FROM prepared_chunks WHERE embedding IS NULL LIMIT ?", (limit,))
    rows = cur.fetchall()
    print(f"🚀 Embedding {len(rows)} chunks...")

    t0 = time.perf_counter()
    updates = []
    for idx, (cid, text) in enumerate(rows, 1):
        # Embed first 150 chars for passage representation
        vec = vectorizer.embed_query(text[:150])
        updates.append((vec.tobytes(), cid))
        
        if len(updates) >= batch_size:
            cur.executemany("UPDATE prepared_chunks SET embedding = ? WHERE chunk_id = ?", updates)
            conn.commit()
            updates.clear()
            print(f"  • Processed {idx}/{len(rows)} chunks ({(idx / (time.perf_counter() - t0)):.1f} chunks/sec)...")

    if updates:
        cur.executemany("UPDATE prepared_chunks SET embedding = ? WHERE chunk_id = ?", updates)
        conn.commit()

    conn.close()
    elapsed = time.perf_counter() - t0
    print(f"✓ Embedded {len(rows)} chunks in {elapsed:.2f}s ({(len(rows) / elapsed):.1f} chunks/sec)!")

if __name__ == "__main__":
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "shamela_corpus.db"))
    populate_vectors(db_file, limit=10000)
