from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Dict, Any
import libsql_client
from app.core.database import get_db_client

router = APIRouter(prefix="/sitemaps", tags=["Sitemaps"])

CHUNK_PARTITION_SIZE = 40000

@router.get("/chunks", response_model=List[int])
async def get_sitemap_chunk_ids(
    part: int = Query(1, ge=1, le=10, description="Partition number (1-indexed)"),
    limit: int = Query(CHUNK_PARTITION_SIZE, ge=1, le=50000, description="Max URLs per partition"),
    client: libsql_client.Client = Depends(get_db_client)
):
    """
    Returns valid, existing chunk IDs in ascending order for sitemap generation.
    Enforces chunk partitioning to comply with the Sitemaps.org 50,000 URL limit.
    """
    offset = (part - 1) * limit
    try:
        res = await client.execute(
            "SELECT chunk_id FROM prepared_chunks ORDER BY chunk_id ASC LIMIT ? OFFSET ?",
            [limit, offset]
        )
        return [row[0] for row in res.rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chunk IDs: {str(e)}")

@router.get("/books", response_model=List[Dict[str, Any]])
async def get_sitemap_books(
    client: libsql_client.Client = Depends(get_db_client)
):
    """
    Returns canonical book records for the books sitemap.
    """
    try:
        res = await client.execute(
            """
            SELECT book_id, title_ar, author_name, author_death_hijri, category_name
            FROM books
            ORDER BY book_id ASC
            """
        )
        books = []
        for row in res.rows:
            books.append({
                "book_id": row[0],
                "title_ar": row[1],
                "author_name": row[2],
                "author_death_hijri": row[3],
                "category_name": row[4]
            })
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch books: {str(e)}")

@router.get("/info", response_model=Dict[str, Any])
async def get_sitemap_info(
    client: libsql_client.Client = Depends(get_db_client)
):
    """
    Returns total chunk and book counts to dynamically compute required sitemap partitions.
    """
    try:
        res_chunks = await client.execute("SELECT count(*) FROM prepared_chunks")
        res_books = await client.execute("SELECT count(*) FROM books")
        total_chunks = res_chunks.rows[0][0] if res_chunks.rows else 0
        total_books = res_books.rows[0][0] if res_books.rows else 0
        
        num_partitions = (total_chunks + CHUNK_PARTITION_SIZE - 1) // CHUNK_PARTITION_SIZE
        
        return {
            "total_chunks": total_chunks,
            "total_books": total_books,
            "partition_size": CHUNK_PARTITION_SIZE,
            "num_chunk_partitions": max(num_partitions, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute sitemap info: {str(e)}")
