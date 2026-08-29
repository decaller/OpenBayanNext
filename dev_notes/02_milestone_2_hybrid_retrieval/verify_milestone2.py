import os
import sys
import time
import asyncio
import numpy as np

# Add apps/api to path (2 levels up from dev_notes/02_milestone_2_hybrid_retrieval/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api")))

from app.core.database import db
from app.core.vectorizer import vectorizer
from app.services.query_expander import build_fts5_query
from app.services.retriever import hybrid_search, vector_matrix_cache
from app.services.merger import merge_contiguous_siblings
from app.schemas.search import SearchResultItem

async def run_milestone2_verification():
    print("="*80)
    print("🚀 OPENBAYAN MILESTONE 2: HYBRID RETRIEVAL & CONTEXT VERIFICATION SUITE")
    print("="*80)

    # 1. Test Lifespan Startup & Warmup
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "shamela_corpus.db"))
    db._db_url = f"file:{db_file}"
    await db.connect()
    
    print("\n[Step 1/6] Testing Vectorizer Warmup & E5 Embeddings...")
    t0 = time.perf_counter()
    vectorizer.warmup()
    t1 = time.perf_counter()
    print(f"✓ Warmup complete in {(t1-t0)*1000:.2f} ms")

    v = vectorizer.embed_query("شروط بيع السلم")
    print(f"✓ Generated Query Embedding: shape={v.shape}, norm={np.linalg.norm(v):.4f}, dtype={v.dtype}")
    assert v.shape == (768,), "Vector must be 768-dimensional"
    assert abs(np.linalg.norm(v) - 1.0) < 1e-4, "Vector must be unit normalized"

    # 2. Test RAM-Cached Vector Matrix Load
    print("\n[Step 2/6] Loading In-Memory Vector Matrix for Fallback...")
    await vector_matrix_cache.load(db.client)
    print(f"✓ Vector Matrix status: loaded={vector_matrix_cache._is_loaded}, rows={len(vector_matrix_cache.chunk_ids)}")

    # 3. Test Morphological Query Expander
    print("\n[Step 3/6] Testing Morphological Query Expansion (Disjunctive Lemmas)...")
    test_queries = [
        "إنما الأعمال بالنيات",
        "شروط بيع السلم",
        "صلاة الوتر"
    ]
    for tq in test_queries:
        expanded = build_fts5_query(tq)
        print(f"  • '{tq}'\n    ↳ FTS5: {expanded}")
        assert "salient_roots_text:" in expanded, "Must target salient_roots_text"
        assert "AND" in expanded or "OR" in expanded, "Must contain boolean logic"

    # 4. Test Sibling Merger Logic & Score Invariants
    print("\n[Step 4/6] Testing Contiguous Sibling Merger & Scoring Invariants...")
    dummy_hits = [
        SearchResultItem(
            chunk_id=101, book_id=1, book_name="Book A", volume_page="ج 1 ص 10", chunk_order=10,
            section_id="sec_1", section_title="Sec 1", breadcrumb="Root > Sec 1",
            text_snippet="Passage 10", full_text="Text of page 10", rrf_score=0.0160, bm25_score=10.0, vector_score=0.85
        ),
        SearchResultItem(
            chunk_id=102, book_id=1, book_name="Book A", volume_page="ج 1 ص 11", chunk_order=11,
            section_id="sec_1", section_title="Sec 1", breadcrumb="Root > Sec 1",
            text_snippet="Passage 11", full_text="Text of page 11", rrf_score=0.0080, bm25_score=5.0, vector_score=0.60
        ),
        SearchResultItem(
            chunk_id=205, book_id=2, book_name="Book B", volume_page="ص 50", chunk_order=50,
            section_id="sec_2", section_title="Sec 2", breadcrumb="Root > Sec 2",
            text_snippet="Passage 50", full_text="Text of page 50", rrf_score=0.0120, bm25_score=8.0, vector_score=0.75
        )
    ]
    merged = merge_contiguous_siblings(dummy_hits, continuity_bonus=1.05)
    print(f"✓ Initial Items: {len(dummy_hits)} -> Merged Items: {len(merged)}")
    assert len(merged) == 2, "Adjacent items (101, 102) must fuse into 1 merged card"
    fused_item = merged[0]
    expected_score = max(0.0160, 0.0080) * 1.05
    print(f"✓ Fused Score: {fused_item.rrf_score:.6f} (Expected: {expected_score:.6f})")
    assert abs(fused_item.rrf_score - expected_score) < 1e-6, "Score formula must be max(A, B) * 1.05"
    assert fused_item.is_merged is True, "is_merged flag must be True"
    assert fused_item.merged_chunk_ids == [101, 102], "Must record merged chunk IDs"
    assert "ج 1 ص 10 - ج 1 ص 11" in fused_item.volume_page, "Must combine page labels"
    assert '<hr class="page-divider"/>' in fused_item.full_text, "Must include visual page divider"

    # 5. Test Live Hybrid Search & Latency Benchmarks
    print("\n[Step 5/6] Benchmarking Live Dual-Path Hybrid Search...")
    benchmark_queries = [
        "شروط بيع السلم",
        "إنما الأعمال بالنيات",
        "صلاة الوتر في السفر",
        "طهارة الماء الراكد",
        "ثبوت الشفعة للشريك"
    ]
    for bq in benchmark_queries:
        res = await hybrid_search(bq, page=1, limit=5, mode="hybrid", merge_siblings=True)
        print(f"\n  Query: '{bq}' | Total Hits: {res.total_hits} | Latency: \033[1;32m{res.took_ms:.3f} ms\033[0m")
        if res.results:
            top = res.results[0]
            print(f"  • Top Match: [{top.book_name}] ({top.volume_page}) | RRF: {top.rrf_score:.5f}")
            print(f"    Breadcrumb: {top.breadcrumb}")
            print(f"    Snippet: \"{top.text_snippet[:120]}...\"")

    # 6. Test Level 1, 2, and 3 Context Resolution
    print("\n[Step 6/6] Testing 3-Tier Context Resolvers & Invariants...")
    # Level 1: Fetch Chunk 72346
    from app.api.chunks import get_chunk_detail, get_surrounding_context
    from app.api.books import get_chapter_stream, get_book_toc, list_books

    chunk_detail = await get_chunk_detail(72346)
    print(f"✓ Level 1 Detail: [{chunk_detail.book_name}] -> {chunk_detail.section_title} ({chunk_detail.volume_page})")

    # Level 2: Surrounding Context ($N \pm 1$)
    surrounding = await get_surrounding_context(72346)
    print(f"✓ Level 2 Surrounding ({len(surrounding.items)} items):")
    for item in surrounding.items:
        marker = "👉 FOCUS" if item.is_focus_chunk else f"   Neighbor {item.chunk_order}"
        print(f"  - [{marker}] Chunk #{item.chunk_id} ({item.volume_page}) | same_sec={item.is_same_section} | same_book={item.is_same_book}")

    # Level 3: Chapter Stream
    chapter_stream = await get_chapter_stream(chunk_detail.book_id, chunk_detail.section_id)
    print(f"✓ Level 3 Chapter Stream: {chapter_stream.section_title} ({chapter_stream.total_chunks} continuous chunks)")

    # TOC Tree
    toc = await get_book_toc(chunk_detail.book_id)
    print(f"✓ Book TOC Tree: {len(toc)} root section nodes")

    # Book catalog
    books = await list_books()
    print(f"✓ Books Catalog: {len(books)} canonical books loaded")

    await db.close()
    print("\n" + "═"*80)
    print("🎉 ALL MILESTONE 2 VERIFICATIONS AND BENCHMARKS PASSED SUCCESSFULLY!")
    print("═"*80)

if __name__ == "__main__":
    asyncio.run(run_milestone2_verification())
