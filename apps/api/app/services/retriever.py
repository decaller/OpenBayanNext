import time
import asyncio
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import libsql_client

from app.core.database import db
from app.core.vectorizer import vectorizer
from app.services.query_expander import build_fts5_query
from app.services.merger import merge_contiguous_siblings
from app.schemas.search import SearchResultItem, SearchResponse

class VectorMatrixCache:
    """
    RAM-Cached In-Memory Vector Matrix for ultra-fast semantic fallback search.
    Stores normalized float32 matrix V in R^(N x 768) and chunk_id index mappings.
    """
    def __init__(self):
        self.chunk_ids: np.ndarray = np.array([], dtype=np.int64)
        self.matrix: Optional[np.ndarray] = None
        self._is_loaded: bool = False

    async def load(self, client: libsql_client.Client):
        if self._is_loaded:
            return
        t0 = time.perf_counter()
        sql = "SELECT chunk_id, embedding FROM prepared_chunks WHERE embedding IS NOT NULL ORDER BY chunk_id ASC"
        res = await client.execute(sql)
        
        if not res.rows:
            # Fallback if embeddings are synthetic or not populated yet
            self._is_loaded = True
            return

        c_ids = []
        vec_list = []
        for row in res.rows:
            c_id, blob = row[0], row[1]
            if blob and len(blob) == 3072:
                vec = np.frombuffer(blob, dtype="<f4")
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                c_ids.append(c_id)
                vec_list.append(vec)

        if vec_list:
            self.chunk_ids = np.array(c_ids, dtype=np.int64)
            self.matrix = np.vstack(vec_list).astype("<f4") # (N, 768)
            t1 = time.perf_counter()
            print(f"✓ Cached {len(c_ids)} dense vectors into RAM matrix in {(t1-t0)*1000:.2f} ms ({self.matrix.nbytes / (1024*1024):.1f} MB)")
        self._is_loaded = True

    def semantic_search(self, query_vec: np.ndarray, top_k: int = 50) -> List[Tuple[int, float]]:
        """Matrix dot product s = V . q in ~2.5 ms."""
        if self.matrix is None or len(self.chunk_ids) == 0:
            return []
        # Cosine similarity via dot product (both V and q are unit normalized)
        scores = np.dot(self.matrix, query_vec)
        top_indices = np.argpartition(scores, -top_k)[-top_k:]
        top_sorted = top_indices[np.argsort(-scores[top_indices])]
        return [(int(self.chunk_ids[i]), float(scores[i])) for i in top_sorted]

vector_matrix_cache = VectorMatrixCache()

async def hybrid_search(
    query: str,
    page: int = 1,
    limit: int = 20,
    mode: str = "hybrid",
    merge_siblings: bool = True,
    book_ids: Optional[List[int]] = None
) -> SearchResponse:
    t_start = time.perf_counter()
    client = db.client

    # 1. Expand Morphological Query for FTS5
    expanded_fts_expr = build_fts5_query(query)
    
    # 2. Embed Query Vector (Fast CPU ONNX)
    query_vec = None
    if mode in ("hybrid", "vector"):
        try:
            query_vec = vectorizer.embed_query(query)
        except Exception as e:
            print(f"⚠️ Vectorizer error: {e}, falling back to pure BM25")
            mode = "fts"

    # 3. Step 1: Execute FTS5 Search
    fts_candidates: Dict[int, Dict[str, Any]] = {}
    fts_ranks: Dict[int, int] = {}

    fetch_buffer_k = max(min(limit * 3, 60), 30)

    if expanded_fts_expr and mode in ("hybrid", "fts"):
        book_filter = ""
        params: List[Any] = [expanded_fts_expr]
        if book_ids:
            placeholders = ",".join("?" for _ in book_ids)
            book_filter = f"AND p.book_id IN ({placeholders})"
            params.extend(book_ids)
            
        sql_fts = f"""
        SELECT 
            p.chunk_id, p.book_id, p.book_name, p.volume_page, p.chunk_order,
            p.section_id, p.section_title, p.breadcrumb, p.raw_text, p.footnotes,
            p.embedding, f.rank
        FROM prepared_chunks_fts f
        JOIN prepared_chunks p ON p.chunk_id = f.rowid
        WHERE prepared_chunks_fts MATCH ?
        {book_filter}
        ORDER BY f.rank
        LIMIT {fetch_buffer_k}
        """
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
                    "embedding": row[10],
                    "bm25_rank": row[11],
                    "bm25_score": -float(row[11]) if row[11] is not None else 0.0,
                    "vector_score": 0.0
                }
        except Exception as e:
            print(f"⚠️ FTS query execution failed: {e}")

    # 4. Dual-Path Vector Re-ranking / Semantic Fallback
    vec_ranks: Dict[int, int] = {}
    
    if mode in ("hybrid", "vector") and query_vec is not None:
        # Path A: Re-rank FTS candidates if we have enough hits
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

        # Path B: Fallback to full RAM matrix if FTS yielded < 10 hits
        elif vector_matrix_cache.matrix is not None and len(vector_matrix_cache.chunk_ids) > 0:
            semantic_hits = vector_matrix_cache.semantic_search(query_vec, top_k=fetch_buffer_k)
            for r_idx, (c_id, sim) in enumerate(semantic_hits, 1):
                vec_ranks[c_id] = r_idx
                if c_id not in fts_candidates:
                    # Fetch missing row details
                    row_res = await client.execute("""
                        SELECT chunk_id, book_id, book_name, volume_page, chunk_order,
                               section_id, section_title, breadcrumb, raw_text, footnotes
                        FROM prepared_chunks WHERE chunk_id = ?
                    """, [c_id])
                    if row_res.rows:
                        r = row_res.rows[0]
                        fts_candidates[c_id] = {
                            "chunk_id": r[0], "book_id": r[1], "book_name": r[2],
                            "volume_page": r[3], "chunk_order": r[4], "section_id": r[5],
                            "section_title": r[6], "breadcrumb": r[7], "raw_text": r[8],
                            "footnotes": r[9], "bm25_score": None, "vector_score": sim
                        }

    # 5. Compute Reciprocal Rank Fusion (RRF) Scores (k=60)
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
            merged_chunk_ids=[item["chunk_id"]],
            merged_page_range=None
        )
        scored_items.append(search_item)

    # Sort candidates by RRF score descending
    scored_items.sort(key=lambda x: x.rrf_score, reverse=True)

    # 6. Apply Contiguous Sibling Merger
    if merge_siblings:
        final_items = merge_contiguous_siblings(scored_items, continuity_bonus=1.05)
    else:
        final_items = scored_items

    # 7. Apply Pagination (page, limit)
    total_hits = len(final_items)
    offset = (page - 1) * limit
    paginated_results = final_items[offset:offset + limit]

    # 8. Enrich Paginated Results with Author metadata and Preceding/Succeeding Chunks (N-1, N+1)
    for p_item in paginated_results:
        try:
            n_res = await client.execute("""
                SELECT p.chunk_id, p.chunk_order, p.raw_text, b.author_name, b.author_death_hijri
                FROM prepared_chunks p
                JOIN books b ON p.book_id = b.book_id
                WHERE p.book_id = ? AND p.chunk_order IN (?, ?, ?)
            """, [p_item.book_id, p_item.chunk_order - 1, p_item.chunk_order, p_item.chunk_order + 1])
            
            for nrow in n_res.rows:
                c_id, c_order, c_text, auth_name, auth_death = nrow[0], nrow[1], nrow[2], nrow[3], nrow[4]
                if not p_item.author_name:
                    p_item.author_name = auth_name
                    p_item.author_death_hijri = auth_death
                if c_order == p_item.chunk_order - 1:
                    p_item.preceding_chunk_id = c_id
                    p_item.preceding_text = c_text
                elif c_order == p_item.chunk_order + 1:
                    p_item.succeeding_chunk_id = c_id
                    p_item.succeeding_text = c_text
        except Exception as e:
            print(f"⚠️ Warning: context enrichment failed for chunk {p_item.chunk_id}: {e}")

    t_end = time.perf_counter()
    took_ms = (t_end - t_start) * 1000

    return SearchResponse(
        query=query,
        expanded_fts_query=expanded_fts_expr,
        mode=mode,
        page=page,
        limit=limit,
        total_hits=total_hits,
        took_ms=round(took_ms, 3),
        results=paginated_results
    )
