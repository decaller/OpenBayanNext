from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.core.database import db
from app.schemas.search import ChunkDetailResponse, SurroundingContextResponse, SurroundingContextItem

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
