from typing import List, Dict
from fastapi import APIRouter, HTTPException, Path
from app.core.database import db
from app.schemas.search import BookSummaryItem, TOCNodeItem, ChapterStreamResponse, ChapterChunkItem

router = APIRouter(prefix="/books", tags=["Books & TOC"])

@router.get("", response_model=List[BookSummaryItem])
async def list_books():
    """
    Returns a summary list of all 60 canonical books with author info and passage counts.
    """
    client = db.client
    sql = """
    SELECT 
        b.book_id, b.shamela_id, b.title_ar, b.author_name, b.author_death_hijri, 
        b.category_name, COUNT(p.chunk_id) as chunk_count
    FROM books b
    LEFT JOIN prepared_chunks p ON b.book_id = p.book_id
    GROUP BY b.book_id
    ORDER BY b.author_death_hijri ASC, b.book_id ASC
    """
    res = await client.execute(sql)
    results: List[BookSummaryItem] = []
    for r in res.rows:
        results.append(BookSummaryItem(
            book_id=r[0],
            shamela_id=r[1],
            title_ar=r[2],
            author_name=r[3],
            author_death_hijri=r[4],
            category_name=r[5],
            chunk_count=r[6]
        ))
    return results

@router.get("/{book_id}/toc", response_model=List[TOCNodeItem])
async def get_book_toc(book_id: int = Path(..., ge=1)):
    """
    Returns the complete hierarchical Table of Contents tree for a book.
    """
    client = db.client
    sql = """
    SELECT section_id, parent_id, title_text, section_level, start_page_id, breadcrumb
    FROM sections
    WHERE book_id = ?
    ORDER BY start_page_id ASC, section_level ASC
    """
    res = await client.execute(sql, [book_id])
    if not res.rows:
        raise HTTPException(status_code=404, detail=f"No sections found for book {book_id}.")

    nodes_by_id: Dict[str, TOCNodeItem] = {}
    root_nodes: List[TOCNodeItem] = []

    for r in res.rows:
        node = TOCNodeItem(
            section_id=r[0],
            parent_id=r[1],
            title_text=r[2],
            section_level=r[3],
            start_page_id=r[4],
            breadcrumb=r[5],
            children=[]
        )
        nodes_by_id[node.section_id] = node

    for node in nodes_by_id.values():
        if node.parent_id and node.parent_id in nodes_by_id:
            nodes_by_id[node.parent_id].children.append(node)
        else:
            root_nodes.append(node)

    return root_nodes

@router.get("/{book_id}/sections/{section_id}/chunks", response_model=ChapterStreamResponse)
async def get_chapter_stream(
    book_id: int = Path(..., ge=1),
    section_id: str = Path(...)
):
    """
    Level 3: Full chapter / section passage stream for continuous reading in the Astro drawer.
    """
    client = db.client
    
    # 1. Fetch section metadata
    sec_res = await client.execute("""
        SELECT s.section_id, s.title_text, s.breadcrumb, b.title_ar
        FROM sections s
        JOIN books b ON s.book_id = b.book_id
        WHERE s.book_id = ? AND s.section_id = ?
    """, [book_id, section_id])
    
    if not sec_res.rows:
        # Fallback to book if intro section
        b_res = await client.execute("SELECT title_ar FROM books WHERE book_id = ?", [book_id])
        if not b_res.rows:
            raise HTTPException(status_code=404, detail=f"Book {book_id} not found.")
        sec_title = "مقدمة الكتاب"
        breadcrumb = f"{b_res.rows[0][0]} > مقدمة الكتاب"
        book_name = b_res.rows[0][0]
    else:
        r = sec_res.rows[0]
        sec_title = r[1]
        breadcrumb = r[2]
        book_name = r[3]

    # 2. Fetch all chunks belonging to this section
    chunks_res = await client.execute("""
        SELECT chunk_id, page_id, volume_page, chunk_order, raw_text, footnotes, is_section_start
        FROM prepared_chunks
        WHERE book_id = ? AND section_id = ?
        ORDER BY chunk_order ASC
    """, [book_id, section_id])

    chunks: List[ChapterChunkItem] = []
    for c in chunks_res.rows:
        chunks.append(ChapterChunkItem(
            chunk_id=c[0],
            page_id=c[1],
            volume_page=c[2],
            chunk_order=c[3],
            raw_text=c[4],
            footnotes=c[5],
            is_section_start=bool(c[6])
        ))

    return ChapterStreamResponse(
        book_id=book_id,
        book_name=book_name,
        section_id=section_id,
        section_title=sec_title,
        breadcrumb=breadcrumb,
        total_chunks=len(chunks),
        chunks=chunks
    )
