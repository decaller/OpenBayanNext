import os
import sys
import json
import time
import sqlite3
import argparse
from pathlib import Path
import numpy as np

from pipeline.stemmer import extract_composite_stems
from pipeline.toc_resolver import TOCResolver
from pipeline.schema import init_db_schema, rebuild_fts_index, finalize_db

def setup_db_connection(db_path: str) -> sqlite3.Connection:
    """Creates an optimized SQLite connection for high-throughput bulk insertion."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            if os.path.exists(f"{db_path}-wal"):
                os.remove(f"{db_path}-wal")
            if os.path.exists(f"{db_path}-shm"):
                os.remove(f"{db_path}-shm")
        except Exception:
            pass

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA page_size = 65536;")
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA cache_size = -64000;") # 64MB cache
    cur.execute("PRAGMA temp_store = MEMORY;")
    cur.execute("PRAGMA journal_mode = MEMORY;") # In-memory during bulk load
    conn.commit()
    return conn

def discover_books(sample_dir: str):
    """Scans sample directories for AuthenticIlm book directories containing book_metadata.json and pages.jsonl."""
    books = []
    auth_dir = os.path.join(sample_dir, "AuthenticIlm_Shamela4_Full_DB")
    if not os.path.exists(auth_dir):
        auth_dir = sample_dir

    for root, dirs, files in os.walk(auth_dir):
        if "pages.jsonl" in files and "book_metadata.json" in files:
            meta_path = os.path.join(root, "book_metadata.json")
            pages_path = os.path.join(root, "pages.jsonl")
            toc_path = os.path.join(root, "toc.jsonl") if "toc.jsonl" in files else None
            books.append({
                "dir": root,
                "meta_path": meta_path,
                "pages_path": pages_path,
                "toc_path": toc_path
            })
    return books

def ingest_corpus(sample_dir: str, db_path: str):
    start_time = time.time()
    print(f"🚀 Starting OpenBayan Ingestion Pipeline")
    print(f"   • Source Directory: {sample_dir}")
    print(f"   • Target Database:  {db_path}")

    conn = setup_db_connection(db_path)
    init_db_schema(conn)

    books = discover_books(sample_dir)
    print(f"📚 Discovered {len(books)} canonical books to ingest.\n")

    cur = conn.cursor()
    global_chunk_id = 1
    total_pages_inserted = 0
    total_sections_inserted = 0

    chunk_insert_sql = """
    INSERT INTO prepared_chunks (
        chunk_id, book_id, book_name, page_id, volume_page, chunk_order,
        section_id, section_level, section_title, breadcrumb,
        raw_text, footnotes, salient_roots_text, is_section_start, embedding
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    book_insert_sql = """
    INSERT INTO books (
        book_id, shamela_id, title_ar, author_name, author_death_hijri, category_name, metadata_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    section_insert_sql = """
    INSERT INTO sections (
        section_id, book_id, parent_id, title_text, section_level, start_page_id, breadcrumb
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    for b_idx, book_info in enumerate(books, 1):
        try:
            with open(book_info["meta_path"], "r", encoding="utf-8", errors="ignore") as f:
                meta = json.load(f)
        except Exception as e:
            print(f"⚠️ Skipping book {book_info['dir']} due to metadata error: {e}")
            continue

        book_id = meta.get("book_id", b_idx)
        shamela_id = meta.get("shamela_id")
        title_ar = meta.get("title_ar", "كتاب غير معنون")
        author_name = meta.get("main_author_name_ar", "غير معروف")
        author_death = meta.get("main_author_death_hijri", 99999)
        category_name = meta.get("category_name_ar", "عام")

        print(f"[{b_idx}/{len(books)}] Ingesting: {title_ar} (Author: {author_name}, d. {author_death} AH)")

        # 1. Insert Book Record
        cur.execute(book_insert_sql, (
            book_id, shamela_id, title_ar, author_name, author_death, category_name, json.dumps(meta, ensure_ascii=False)
        ))

        # 2. Resolve TOC Tree & Insert Sections
        toc_resolver = TOCResolver(book_id, title_ar, book_info["toc_path"])
        sections = toc_resolver.get_all_sections_for_db()
        for sec in sections:
            cur.execute(section_insert_sql, (
                sec["section_id"], sec["book_id"], sec["parent_id"],
                sec["title_text"], sec["section_level"], sec["start_page_id"], sec["breadcrumb"]
            ))
        total_sections_inserted += len(sections)

        # 3. Stream & Process Pages
        chunk_batch = []
        chunk_order = 1
        with open(book_info["pages_path"], "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    page_data = json.loads(line)
                except Exception:
                    # Gracefully skip incomplete/truncated lines at end of sample files
                    continue

                page_id = page_data.get("page_id", global_chunk_id)
                part = page_data.get("part")
                page_num = page_data.get("page_num", 1)
                body = page_data.get("body", "")
                footnotes = page_data.get("footnotes")

                if not body or len(body.strip()) < 5:
                    continue

                # Format volume and page string (e.g. "ج 1 ص 15" or "ص 15")
                if part is not None:
                    vol_page = f"ج {part} ص {page_num}"
                else:
                    vol_page = f"ص {page_num}"

                # Resolve TOC Interval & Breadcrumb
                sec_id, sec_level, sec_title, breadcrumb, is_sec_start = toc_resolver.resolve_page(page_id)

                # Generate normalized composite lemmas + roots for FTS5
                salient_roots = extract_composite_stems(body)

                # Vector placeholder (None for now or byte blob)
                embedding_bytes = None

                chunk_batch.append((
                    global_chunk_id, book_id, title_ar, page_id, vol_page, chunk_order,
                    sec_id, sec_level, sec_title, breadcrumb,
                    body, footnotes, salient_roots, 1 if is_sec_start else 0, embedding_bytes
                ))

                global_chunk_id += 1
                chunk_order += 1
                total_pages_inserted += 1

                if len(chunk_batch) >= 2000:
                    cur.executemany(chunk_insert_sql, chunk_batch)
                    chunk_batch.clear()

            if chunk_batch:
                cur.executemany(chunk_insert_sql, chunk_batch)
                chunk_batch.clear()

        conn.commit()

    # 4. Rebuild FTS5 Index in Single Bulk Pass
    print("\n⚡ Rebuilding FTS5 Full-Text Search Index...")
    fts_start = time.time()
    rebuild_fts_index(conn)
    print(f"✓ FTS5 Index rebuilt in {time.time() - fts_start:.2f}s")

    # 5. Finalize Database for Read-Only Immutable Mounting
    print("🔒 Finalizing & hard-locking database for read-only Docker mounting...")
    finalize_db(conn)
    conn.close()

    elapsed = time.time() - start_time
    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"\n========================================================")
    print(f"🎉 Ingestion Complete!")
    print(f"   • Total Books:        {len(books)}")
    print(f"   • Total Sections:     {total_sections_inserted}")
    print(f"   • Total Chunks/Pages: {total_pages_inserted}")
    print(f"   • Database File Size: {db_size_mb:.2f} MB")
    print(f"   • Elapsed Time:       {elapsed:.2f}s ({total_pages_inserted / elapsed:.0f} pages/sec)")
    print(f"========================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenBayan Classical Arabic Ingestion Pipeline")
    parser.add_argument("--sample-dir", default="data/samples", help="Path to samples directory")
    parser.add_argument("--db-path", default="data/shamela_corpus.db", help="Target SQLite DB path")
    args = parser.parse_args()

    ingest_corpus(args.sample_dir, args.db_path)
