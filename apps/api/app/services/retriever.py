import time
import re
from typing import List, Optional, Dict, Any
import numpy as np
from app.core.database import get_db_client
from app.schemas.search import SearchResponse, SearchResultItem
from app.core.vectorizer import vectorizer
from app.services.merger import merge_contiguous_siblings
from app.services.citation_router import parse_scripture_citation, resolve_pinned_citation

class VectorMatrixCache:
    """
    In-memory Dense Vector Matrix for ultra-low-latency semantic retrieval (<4ms).
    Holds normalized vectors in a contiguous NumPy array.
    """
    def __init__(self):
        self.chunk_ids: List[int] = []
        self.matrix: Optional[np.ndarray] = None
        self.is_loaded: bool = False

    async def load_if_needed(self):
        if self.is_loaded:
            return
        client = await get_db_client()
        t0 = time.perf_counter()
        
        # Load pre-computed 768-dim embeddings from SQLite
        res = await client.execute("SELECT chunk_id, embedding FROM prepared_chunks WHERE embedding IS NOT NULL")
        chunk_ids = []
        vectors = []
        
        for row in res.rows:
            c_id, blob = row[0], row[1]
            if blob and len(blob) == 3072: # 768 * 4 bytes float32
                vec = np.frombuffer(blob, dtype="<f4")
                chunk_ids.append(c_id)
                vectors.append(vec)

        if vectors:
            self.chunk_ids = chunk_ids
            self.matrix = np.vstack(vectors).astype(np.float32)
            self.is_loaded = True
            took_ms = (time.perf_counter() - t0) * 1000
            print(f"✓ Cached {len(chunk_ids)} dense vectors into RAM matrix in {took_ms:.2f} ms ({self.matrix.nbytes / (1024*1024):.1f} MB)")

    def semantic_search(self, query_vec: np.ndarray, top_k: int = 40) -> List[tuple[int, float]]:
        if self.matrix is None or len(self.chunk_ids) == 0:
            return []
        # Matrix-vector dot product (cosine similarity since normalized)
        sims = np.dot(self.matrix, query_vec)
        top_indices = np.argpartition(sims, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(-sims[top_indices])]
        
        return [(self.chunk_ids[idx], float(sims[idx])) for idx in top_indices]

vector_matrix_cache = VectorMatrixCache()

async def search_hybrid(
    query: str,
    page: int = 1,
    limit: int = 60,
    mode: str = "hybrid",
    book_ids: Optional[List[int]] = None,
    category: Optional[str] = None,
    era: Optional[str] = None,
    tradition: Optional[str] = None,
    merge_siblings: bool = True
) -> SearchResponse:
    """
    Executes high-performance hybrid retrieval combining CTE-driven SQLite FTS5 BM25,
    dense vector re-ranking, faceted metadata predicates, and citation routing interceptor.
    """
    t_start = time.perf_counter()
    client = await get_db_client()

    # Pre-warm vector cache
    await vector_matrix_cache.load_if_needed()

    # 1. Check Scripture Citation Interceptor (Ayah / Hadith lookup)
    pinned_citation = None
    citation_meta = parse_scripture_citation(query)
    if citation_meta:
        pinned_citation = await resolve_pinned_citation(citation_meta)

    # 2. Build Query Formulations & Morphological Root Expansion
    clean_query = re.sub(r"[^\u0621-\u064A0-9\s]", " ", query).strip()
    query_tokens = [t for t in clean_query.split() if len(t) > 1]
    
    expanded_fts_expr = None
    if query_tokens:
        fts_terms = []
        for t in query_tokens:
            bare_t = re.sub(r"^(ال|بال|كال|فال|لل|وال)", "", t)
            if len(bare_t) >= 3:
                fts_terms.append(f'("{t}"* OR "{bare_t}"*)')
            else:
                fts_terms.append(f'"{t}"*')
        expanded_fts_expr = " AND ".join(fts_terms)

    # 3. Resolve Era Hijri bounds
    min_hijri = None
    max_hijri = None
    if era == "early":
        max_hijri = 300
    elif era == "classical":
        min_hijri = 301
        max_hijri = 700
    elif era == "late":
        min_hijri = 701

    # Normalize category / tradition
    filter_category = category if category and category != "all" else None
    filter_tradition = tradition if tradition and tradition != "all" else None

    # 4. Embed Query Vector (Fast CPU ONNX)
    query_vec = None
    if mode in ("hybrid", "vector"):
        try:
            query_vec = vectorizer.embed_query(query)
        except Exception as e:
            print(f"⚠️ Vectorizer error: {e}, falling back to pure BM25")
            mode = "fts"

    # 5. Execute CTE-driven FTS5 Search with Pushed-Down Relational Facet Filters
    fts_candidates: Dict[int, Dict[str, Any]] = {}
    fts_ranks: Dict[int, int] = {}
    fetch_buffer_k = max(min(limit * 3, 100), 40)

    if expanded_fts_expr and mode in ("hybrid", "fts"):
        book_filter = ""
        params: List[Any] = [expanded_fts_expr]
        if book_ids:
            placeholders = ",".join("?" for _ in book_ids)
            book_filter = f"AND p.book_id IN ({placeholders})"
            params.extend(book_ids)
            
        sql_fts = f"""
        WITH fts_matches AS (
            SELECT rowid AS chunk_id, rank AS bm25_rank
            FROM prepared_chunks_fts
            WHERE prepared_chunks_fts MATCH ?
            LIMIT 150
        )
        SELECT 
            p.chunk_id, p.book_id, b.title_ar, p.volume_page, p.chunk_order,
            p.section_id, p.section_title, p.breadcrumb, p.raw_text, p.footnotes,
            p.is_section_start, b.category_name, b.author_name, b.author_death_hijri,
            b.tradition, b.era_tag, p.embedding, m.bm25_rank
        FROM fts_matches m
        JOIN prepared_chunks p ON m.chunk_id = p.chunk_id
        JOIN books b ON p.book_id = b.book_id
        WHERE (? IS NULL OR b.category_name = ?)
          AND (? IS NULL OR b.author_death_hijri >= ?)
          AND (? IS NULL OR b.author_death_hijri <= ?)
          AND (? IS NULL OR b.tradition = ?)
          {book_filter}
        ORDER BY m.bm25_rank
        LIMIT {fetch_buffer_k};
        """
        params.extend([
            filter_category, filter_category,
            min_hijri, min_hijri,
            max_hijri, max_hijri,
            filter_tradition, filter_tradition
        ])

        try:
            res_fts = await client.execute(sql_fts, params)
            for rank_idx, row in enumerate(res_fts.rows, 1):
                chunk_id = row[0]
                fts_ranks[chunk_id] = rank_idx
                fts_candidates[chunk_id] = {
                    "chunk_id": chunk_id,
                    "book_id": row[1],
                    "book_name": row[2],
                    "volume_page": row[3],
                    "chunk_order": row[4],
                    "section_id": row[5],
                    "section_title": row[6],
                    "breadcrumb": row[7],
                    "raw_text": row[8],
                    "footnotes": row[9],
                    "is_section_start": bool(row[10]),
                    "category_name": row[11],
                    "author_name": row[12],
                    "author_death_hijri": row[13],
                    "author_tradition": row[14],
                    "era_tag": row[15],
                    "embedding": row[16],
                    "bm25_rank": row[17],
                    "bm25_score": -float(row[17]) if row[17] is not None else 0.0,
                    "vector_score": 0.0
                }
        except Exception as e:
            print(f"⚠️ FTS query execution failed: {e}")

    # 6. Dual-Path Vector Re-ranking / Semantic Fallback
    vec_ranks: Dict[int, int] = {}
    
    if mode in ("hybrid", "vector") and query_vec is not None:
        if len(fts_candidates) >= 10:
            scored_candidates = []
            for c_id, item in fts_candidates.items():
                emb_blob = item["embedding"]
                if emb_blob and len(emb_blob) == 3072:
                    vec = np.frombuffer(emb_blob, dtype="<f4")
                    sim = float(np.dot(vec, query_vec))
                    item["vector_score"] = sim
                    scored_candidates.append((c_id, sim))
                else:
                    item["vector_score"] = 0.0
                    scored_candidates.append((c_id, 0.0))

            # Rank by vector cosine similarity
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            for r_idx, (c_id, _) in enumerate(scored_candidates, 1):
                vec_ranks[c_id] = r_idx

        # Semantic fallback to in-memory matrix
        elif vector_matrix_cache.matrix is not None and len(vector_matrix_cache.chunk_ids) > 0:
            semantic_hits = vector_matrix_cache.semantic_search(query_vec, top_k=fetch_buffer_k)
            for r_idx, (c_id, sim) in enumerate(semantic_hits, 1):
                vec_ranks[c_id] = r_idx
                if c_id not in fts_candidates:
                    row_res = await client.execute("""
                        SELECT p.chunk_id, p.book_id, b.title_ar, p.volume_page, p.chunk_order,
                               p.section_id, p.section_title, p.breadcrumb, p.raw_text, p.footnotes,
                               p.is_section_start, b.category_name, b.author_name, b.author_death_hijri,
                               b.tradition, b.era_tag
                        FROM prepared_chunks p
                        JOIN books b ON p.book_id = b.book_id
                        WHERE p.chunk_id = ?
                          AND (? IS NULL OR b.category_name = ?)
                          AND (? IS NULL OR b.author_death_hijri >= ?)
                          AND (? IS NULL OR b.author_death_hijri <= ?)
                          AND (? IS NULL OR b.tradition = ?)
                    """, [
                        c_id,
                        filter_category, filter_category,
                        min_hijri, min_hijri,
                        max_hijri, max_hijri,
                        filter_tradition, filter_tradition
                    ])
                    if row_res.rows:
                        r = row_res.rows[0]
                        fts_candidates[c_id] = {
                            "chunk_id": r[0], "book_id": r[1], "book_name": r[2],
                            "volume_page": r[3], "chunk_order": r[4], "section_id": r[5],
                            "section_title": r[6], "breadcrumb": r[7], "raw_text": r[8],
                            "footnotes": r[9], "is_section_start": bool(r[10]),
                            "category_name": r[11], "author_name": r[12],
                            "author_death_hijri": r[13], "author_tradition": r[14],
                            "era_tag": r[15], "bm25_score": None, "vector_score": sim
                        }

    # 7. Compute Reciprocal Rank Fusion (RRF) Scores (k=60)
    all_candidate_ids = set(fts_candidates.keys())
    scored_items: List[SearchResultItem] = []

    k_rrf = 60.0
    w_bm25 = 0.5
    w_vec = 0.5

    for c_id in all_candidate_ids:
        item = fts_candidates[c_id]
        r_bm25 = fts_ranks.get(c_id, 1000)
        r_vec = vec_ranks.get(c_id, 1000)

        if mode == "fts":
            rrf = 1.0 / (k_rrf + r_bm25)
        elif mode == "vector":
            rrf = 1.0 / (k_rrf + r_vec)
        else:
            rrf = (w_bm25 / (k_rrf + r_bm25)) + (w_vec / (k_rrf + r_vec))

        raw_text = item["raw_text"]
        snippet = raw_text[:300].replace("\r", " ").replace("\n", " ") + ("..." if len(raw_text) > 300 else "")

        search_item = SearchResultItem(
            chunk_id=item["chunk_id"],
            book_id=item["book_id"],
            book_name=item["book_name"],
            author_name=item.get("author_name"),
            author_death_hijri=item.get("author_death_hijri"),
            category_name=item.get("category_name"),
            author_tradition=item.get("author_tradition"),
            era_tag=item.get("era_tag"),
            volume_page=item["volume_page"],
            chunk_order=item["chunk_order"],
            section_id=item["section_id"],
            section_title=item["section_title"],
            breadcrumb=item["breadcrumb"],
            text_snippet=snippet,
            full_text=raw_text,
            footnotes=item.get("footnotes"),
            bm25_score=item.get("bm25_score"),
            vector_score=item.get("vector_score"),
            rrf_score=rrf,
            is_merged=False,
            is_section_start=item.get("is_section_start", False),
            merged_chunk_ids=[item["chunk_id"]],
            merged_page_range=None
        )
        scored_items.append(search_item)

    # Sort candidates by RRF score descending
    scored_items.sort(key=lambda x: x.rrf_score, reverse=True)

    # 8. Apply Contiguous Sibling Merger
    if merge_siblings:
        final_items = merge_contiguous_siblings(scored_items, continuity_bonus=1.05)
    else:
        final_items = scored_items

    # 9. Apply Result Limiting
    total_hits = len(final_items)
    paginated_results = final_items[:limit]

    # 10. Enrich Results with Surrounding Preceding/Succeeding Chunks (N-1, N+1)
    for p_item in paginated_results:
        try:
            n_res = await client.execute("""
                SELECT chunk_id, chunk_order, raw_text
                FROM prepared_chunks
                WHERE book_id = ? AND chunk_order IN (?, ?)
            """, [p_item.book_id, p_item.chunk_order - 1, p_item.chunk_order + 1])
            
            for nrow in n_res.rows:
                c_id, c_order, c_text = nrow[0], nrow[1], nrow[2]
                if c_order == p_item.chunk_order - 1:
                    p_item.preceding_chunk_id = c_id
                    p_item.preceding_text = c_text
                elif c_order == p_item.chunk_order + 1:
                    p_item.succeeding_chunk_id = c_id
                    p_item.succeeding_text = c_text
        except Exception as e:
            print(f"⚠️ Context enrichment failed for chunk {p_item.chunk_id}: {e}")

    t_end = time.perf_counter()
    took_ms = (t_end - t_start) * 1000

    return SearchResponse(
        query=query,
        expanded_fts_query=expanded_fts_expr,
        mode=mode,
        category=category,
        era=era,
        tradition=tradition,
        page=page,
        limit=limit,
        total_hits=total_hits,
        took_ms=round(took_ms, 3),
        pinned_citation=pinned_citation,
        results=paginated_results
    )
