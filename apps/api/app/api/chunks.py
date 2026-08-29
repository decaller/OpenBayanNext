from typing import List
from fastapi import APIRouter, HTTPException, Path, Query
from app.core.database import db
from app.schemas.search import (
    ChunkDetailResponse, 
    SurroundingContextResponse, 
    SurroundingContextItem,
    ChapterChunkItem
)

router = APIRouter(prefix="/chunks", tags=["Chunks & Context"])

@router.get("/{chunk_id}", response_model=ChunkDetailResponse)
async def get_chunk_detail(chunk_id: int = Path(..., ge=1, description="Unique chunk ID")):
    """
    Level 1: Fetches a single passage with full text, footnotes, section breadcrumbs, and author metadata.
    """
    client = db.client
    sql = """
    SELECT 
        p.chunk_id, p.book_id, p.book_name, b.author_name, b.author_death_hijri, b.category_name,
        p.volume_page, p.chunk_order, p.section_id, p.section_level, p.section_title,
        p.breadcrumb, p.raw_text, p.footnotes
    FROM prepared_chunks p
    JOIN books b ON p.book_id = b.book_id
    WHERE p.chunk_id = ?
    """
    res = await client.execute(sql, [chunk_id])
    if not res.rows:
        raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found.")

    r = res.rows[0]
    return ChunkDetailResponse(
        chunk_id=r[0],
        book_id=r[1],
        book_name=r[2],
        author_name=r[3],
        author_death_hijri=r[4],
        category_name=r[5],
        volume_page=r[6],
        chunk_order=r[7],
        section_id=r[8],
        section_level=r[9],
        section_title=r[10],
        breadcrumb=r[11],
        raw_text=r[12],
        footnotes=r[13]
    )

@router.get("/{chunk_id}/surrounding", response_model=SurroundingContextResponse)
async def get_surrounding_context(chunk_id: int = Path(..., ge=1, description="Unique chunk ID")):
    """
    Level 2: Returns target chunk + immediate neighboring pages (N-1, N, N+1) within the book.
    Includes `is_same_section` and `is_same_book` flags for UI chapter boundary rendering.
    """
    client = db.client
    
    # 1. Fetch target chunk
    target_sql = """
    SELECT chunk_id, book_id, book_name, chunk_order, section_id, section_title
    FROM prepared_chunks
    WHERE chunk_id = ?
    """
    res_target = await client.execute(target_sql, [chunk_id])
    if not res_target.rows:
        raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found.")

    t = res_target.rows[0]
    t_id, t_book_id, t_book_name, t_order, t_sec_id, t_sec_title = t[0], t[1], t[2], t[3], t[4], t[5]

    # 2. Fetch N-1, N, N+1 sibling chunks from same book
    siblings_sql = """
    SELECT 
        chunk_id, chunk_order, volume_page, section_id, section_title, raw_text, footnotes
    FROM prepared_chunks
    WHERE book_id = ? AND chunk_order BETWEEN ? AND ?
    ORDER BY chunk_order ASC
    """
    res_siblings = await client.execute(siblings_sql, [t_book_id, t_order - 1, t_order + 1])

    items: List[SurroundingContextItem] = []
    for row in res_siblings.rows:
        s_id = row[0]
        s_order = row[1]
        s_vol = row[2]
        s_sec_id = row[3]
        s_sec_title = row[4]
        s_text = row[5]
        s_fn = row[6]

        items.append(SurroundingContextItem(
            chunk_id=s_id,
            chunk_order=s_order,
            volume_page=s_vol,
            section_id=s_sec_id,
            section_title=s_sec_title,
            raw_text=s_text,
            footnotes=s_fn,
            is_focus_chunk=(s_id == t_id),
            is_same_section=(s_sec_id == t_sec_id),
            is_same_book=True
        ))

    return SurroundingContextResponse(
        focus_chunk_id=t_id,
        book_id=t_book_id,
        book_name=t_book_name,
        section_id=t_sec_id,
        section_title=t_sec_title,
        items=items
    )

@router.get("/{chunk_id}/expand", response_model=List[ChapterChunkItem])
async def expand_chunk_context(
    chunk_id: int = Path(..., ge=1, description="Reference chunk ID"),
    direction: str = Query(..., pattern="^(before|after)$", description="'before' to fetch earlier pages, 'after' for subsequent"),
    limit: int = Query(5, ge=1, le=20, description="Number of adjacent chunks to fetch")
):
    """
    Fetches contiguous preceding or succeeding chunks in the same book.
    Used by the Reader Drawer to dynamically expand context backwards or forwards.
    """
    client = db.client
    
    # 1. Fetch reference chunk order and book_id
    ref_res = await client.execute("SELECT book_id, chunk_order FROM prepared_chunks WHERE chunk_id = ?", [chunk_id])
    if not ref_res.rows:
        raise HTTPException(status_code=404, detail=f"Reference chunk {chunk_id} not found.")

    book_id = ref_res.rows[0][0]
    chunk_order = ref_res.rows[0][1]

    if direction == "before":
        sql = """
        SELECT chunk_id, page_id, volume_page, chunk_order, raw_text, footnotes, is_section_start
        FROM prepared_chunks
        WHERE book_id = ? AND chunk_order < ?
        ORDER BY chunk_order DESC
        LIMIT ?
        """
        res = await client.execute(sql, [book_id, chunk_order, limit])
        # Reverse to maintain chronological reading order
        rows = list(reversed(res.rows))
    else:
        sql = """
        SELECT chunk_id, page_id, volume_page, chunk_order, raw_text, footnotes, is_section_start
        FROM prepared_chunks
        WHERE book_id = ? AND chunk_order > ?
        ORDER BY chunk_order ASC
        LIMIT ?
        """
        res = await client.execute(sql, [book_id, chunk_order, limit])
        rows = res.rows

    chunks: List[ChapterChunkItem] = []
    for c in rows:
        chunks.append(ChapterChunkItem(
            chunk_id=c[0],
            page_id=c[1],
            volume_page=c[2],
            chunk_order=c[3],
            raw_text=c[4],
            footnotes=c[5],
            is_section_start=bool(c[6])
        ))

    return chunks
