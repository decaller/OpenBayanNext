from typing import List, Optional, Literal
from fastapi import APIRouter, Query, HTTPException
from app.services.retriever import search_hybrid
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=SearchResponse)
async def search_endpoint(
    q: str = Query(..., min_length=1, description="Search query string (Arabic or transliterated)"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(60, ge=1, le=100, description="Number of results per page"),
    mode: Literal["hybrid", "fts", "vector"] = Query("hybrid", description="Retrieval mode"),
    category: Optional[str] = Query(None, description="Discipline/Category filter (e.g. 'التفسير', 'شروح الحديث', 'الفقه الشافعي')"),
    era: Optional[Literal["all", "early", "classical", "late"]] = Query(None, description="Chronological era filter"),
    tradition: Optional[Literal["all", "athari_salafi", "classical_jumhur"]] = Query(None, description="Theological/Ideological tradition filter"),
    merge_siblings: bool = Query(True, description="Fuse adjacent contiguous pages into unified cards"),
    book_ids: Optional[str] = Query(None, description="Comma-separated book IDs to filter (e.g. '1,3,5')")
):
    """
    High-Performance Hybrid & Faceted Search Endpoint:
    Combines CTE-driven FTS5 BM25 lexical ranking, CPU E5 dense vector cosine similarity via RRF,
    metadata faceting (Category, Era, Tradition), and direct scripture citation routing.
    """
    parsed_book_ids = None
    if book_ids:
        try:
            parsed_book_ids = [int(b.strip()) for b in book_ids.split(",") if b.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid book_ids format. Expected comma-separated integers.")

    return await search_hybrid(
        query=q,
        page=page,
        limit=limit,
        mode=mode,
        category=category,
        era=era,
        tradition=tradition,
        merge_siblings=merge_siblings,
        book_ids=parsed_book_ids
    )
