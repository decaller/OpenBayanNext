#!/usr/bin/env python3
"""
OpenBayan Classical Arabic Search CLI & Diagnostic Tool
"""

import os
import sys
import time
import argparse
import sqlite3

# Add apps/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api")))
from pipeline.stemmer import normalize_arabic, extract_composite_stems

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "shamela_corpus.db"))

def highlight_keywords(text: str, keywords: list, max_len: int = 300) -> str:
    snippet = text.replace("\r", " ").replace("\n", " ")
    if len(snippet) > max_len:
        first_pos = -1
        for kw in keywords:
            pos = snippet.find(kw)
            if pos != -1 and (first_pos == -1 or pos < first_pos):
                first_pos = pos
        if first_pos != -1:
            start = max(0, first_pos - 60)
            snippet = ("..." if start > 0 else "") + snippet[start:start + max_len] + "..."
        else:
            snippet = snippet[:max_len] + "..."
            
    for kw in keywords:
        snippet = snippet.replace(kw, f"\033[1;33m{kw}\033[0m")
    return snippet

def search_corpus(query: str, limit: int = 5):
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}. Run pipeline.ingest first.")
        return

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro&immutable=1", uri=True)
    cur = conn.cursor()

    # Extract stems and roots for robust classical query matching
    composite_tokens = extract_composite_stems(query).split()
    if not composite_tokens:
        norm_query = normalize_arabic(query)
        composite_tokens = [w for w in norm_query.split() if len(w) >= 2]
        
    if not composite_tokens:
        print("⚠️ No valid Arabic search terms entered.")
        return

    # Use first few salient tokens for intersection
    search_tokens = composite_tokens[:4]
    fts_match_expr = f"salient_roots_text: ({' AND '.join(search_tokens)})"

    sql = """
    SELECT 
        p.chunk_id, p.book_id, p.book_name, p.volume_page, p.chunk_order,
        p.section_title, p.breadcrumb, p.raw_text, p.footnotes, f.rank
    FROM prepared_chunks_fts f
    JOIN prepared_chunks p ON p.chunk_id = f.rowid
    WHERE prepared_chunks_fts MATCH ?
    ORDER BY f.rank
    LIMIT ?
    """

    t0 = time.perf_counter()
    rows = cur.execute(sql, (fts_match_expr, limit)).fetchall()
    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000

    print("\n" + "═"*80)
    print(f"🔍 Search Query:  \033[1;36m{query}\033[0m")
    print(f"⚡ FTS5 Match:    \033[90m{fts_match_expr}\033[0m")
    print(f"⏱️ Execution:     \033[1;32m{latency_ms:.3f} ms\033[0m | Total Results: \033[1m{len(rows)}\033[0m")
    print("═"*80)

    if not rows:
        print("  (No matches found. Try alternative classical terms or roots)")
        return

    for idx, row in enumerate(rows, 1):
        chunk_id, book_id, book_name, vol_page, chunk_order, sec_title, breadcrumb, raw_text, footnotes, rank = row
        print(f"\n\033[1;32m[{idx}]\033[0m \033[1;37m{book_name}\033[0m  \033[90m({vol_page})\033[0m  \033[33m[BM25 Rank: {rank:.2f}]\033[0m")
        print(f"    📁 \033[34m{breadcrumb}\033[0m")
        print(f"    📖 {highlight_keywords(raw_text, search_tokens, max_len=280)}")
        if footnotes:
            fn_snippet = footnotes.replace('\r', ' ').replace('\n', ' ')[:100]
            print(f"    📝 \033[90mFootnotes: {fn_snippet}...\033[0m")
        print("    " + "─"*76)

    conn.close()

def get_surrounding_context(chunk_id: int):
    """Fetches Level-2 adjacent sibling passages (N-1, N, N+1)."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro&immutable=1", uri=True)
    cur = conn.cursor()
    
    target = cur.execute("""
        SELECT book_id, chunk_order, book_name, section_title, raw_text
        FROM prepared_chunks WHERE chunk_id = ?
    """, (chunk_id,)).fetchone()
    
    if not target:
        print(f"Chunk {chunk_id} not found.")
        return
        
    book_id, chunk_order, book_name, sec_title, text = target
    
    siblings = cur.execute("""
        SELECT chunk_id, chunk_order, volume_page, section_title, raw_text
        FROM prepared_chunks
        WHERE book_id = ? AND chunk_order BETWEEN ? AND ?
        ORDER BY chunk_order ASC
    """, (book_id, chunk_order - 1, chunk_order + 1)).fetchall()
    
    print("\n" + "═"*80)
    print(f"📜 Level-2 Surrounding Context for Chunk #{chunk_id} in [{book_name}]")
    print("═"*80)
    for s_id, s_order, s_vol, s_sec, s_text in siblings:
        marker = "👉 [FOCUS HIT]" if s_id == chunk_id else f"   [Neighbor {s_order}]"
        print(f"\n{marker} Chunk #{s_id} | {s_vol} | Section: {s_sec}")
        print(f"   \"{s_text[:200].replace(chr(10), ' ')}...\"")
    conn.close()

def run_test_suite():
    queries = [
        "شروط بيع السلم",
        "صلاة الوتر في السفر",
        "طهارة الماء الراكد",
        "عجائب القلب والروح",
        "ثبوت الشفعة للشريك",
        "إنما الأعمال بالنيات",
        "تفسير آية الكرسي"
    ]
    for q in queries:
        search_corpus(q, limit=3)
        time.sleep(0.05)

def main():
    parser = argparse.ArgumentParser(description="OpenBayan Search CLI")
    parser.add_argument("query", nargs="?", help="Arabic query to search")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    parser.add_argument("--context", type=int, help="Fetch surrounding context for chunk_id")
    parser.add_argument("--test-suite", action="store_true", help="Run automated test suite")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive search mode")
    args = parser.parse_args()

    if args.context:
        get_surrounding_context(args.context)
    elif args.test_suite:
        run_test_suite()
    elif args.interactive:
        print("\n🕌 OpenBayan Classical Arabic Search Interactive CLI (Type 'exit' to quit)\n")
        while True:
            try:
                q = input("\033[1;36mOpenBayan Search > \033[0m").strip()
                if q.lower() in ("exit", "quit", "q"):
                    break
                if q:
                    search_corpus(q, limit=args.limit)
            except (KeyboardInterrupt, EOFError):
                break
    elif args.query:
        search_corpus(args.query, limit=args.limit)
    else:
        run_test_suite()

if __name__ == "__main__":
    main()
