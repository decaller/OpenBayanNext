from typing import List, Optional
from pydantic import BaseModel, Field

class SearchResultItem(BaseModel):
    chunk_id: int
    book_id: int
    book_name: str
    volume_page: str
    chunk_order: int
    section_id: str
    section_title: str
    breadcrumb: str
    text_snippet: str
    full_text: str
    footnotes: Optional[str] = None
    bm25_score: Optional[float] = None
    vector_score: Optional[float] = None
    rrf_score: float
    is_merged: bool = False
    merged_chunk_ids: List[int] = Field(default_factory=list)
    merged_page_range: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    expanded_fts_query: str
    mode: str
    page: int
    limit: int
    total_hits: int
    took_ms: float
    results: List[SearchResultItem]

class ChunkDetailResponse(BaseModel):
    chunk_id: int
    book_id: int
    book_name: str
    author_name: str
    author_death_hijri: int
    category_name: str
    volume_page: str
    chunk_order: int
    section_id: str
    section_level: int
    section_title: str
    breadcrumb: str
    raw_text: str
    footnotes: Optional[str] = None

class SurroundingContextItem(BaseModel):
    chunk_id: int
    chunk_order: int
    volume_page: str
    section_id: str
    section_title: str
    raw_text: str
    footnotes: Optional[str] = None
    is_focus_chunk: bool = False
    is_same_section: bool = True
    is_same_book: bool = True

class SurroundingContextResponse(BaseModel):
    focus_chunk_id: int
    book_id: int
    book_name: str
    section_id: str
    section_title: str
    items: List[SurroundingContextItem]

class ChapterChunkItem(BaseModel):
    chunk_id: int
    page_id: int
    volume_page: str
    chunk_order: int
    raw_text: str
    footnotes: Optional[str] = None
    is_section_start: bool = False

class ChapterStreamResponse(BaseModel):
    book_id: int
    book_name: str
    section_id: str
    section_title: str
    breadcrumb: str
    total_chunks: int
    chunks: List[ChapterChunkItem]

class BookSummaryItem(BaseModel):
    book_id: int
    shamela_id: Optional[int] = None
    title_ar: str
    author_name: str
    author_death_hijri: int
    category_name: str
    chunk_count: int

class TOCNodeItem(BaseModel):
    section_id: str
    parent_id: Optional[str] = None
    title_text: str
    section_level: int
    start_page_id: int
    breadcrumb: str
    children: List['TOCNodeItem'] = Field(default_factory=list)
