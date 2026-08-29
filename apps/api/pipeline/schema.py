SCHEMA_DDL = """
-- 1. Master Books Metadata Table
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    shamela_id INTEGER,
    title_ar TEXT NOT NULL,
    author_name TEXT NOT NULL,
    author_death_hijri INTEGER,
    category_name TEXT NOT NULL,
    metadata_json TEXT
);

-- 2. Hierarchical TOC Section Nodes Table
CREATE TABLE IF NOT EXISTS sections (
    section_id TEXT PRIMARY KEY,
    book_id INTEGER NOT NULL,
    parent_id TEXT,
    title_text TEXT NOT NULL,
    section_level INTEGER NOT NULL,
    start_page_id INTEGER NOT NULL,
    breadcrumb TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 3. Passages / Pages Content Table
CREATE TABLE IF NOT EXISTS prepared_chunks (
    chunk_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    book_name TEXT NOT NULL,                  -- Denormalized for zero-join fast search
    page_id INTEGER NOT NULL,
    volume_page TEXT NOT NULL,
    chunk_order INTEGER NOT NULL,              -- Monotonic reading sequence
    section_id TEXT NOT NULL,
    section_level INTEGER NOT NULL,
    section_title TEXT NOT NULL,
    breadcrumb TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    footnotes TEXT,
    salient_roots_text TEXT NOT NULL,
    is_section_start BOOLEAN DEFAULT 0,
    embedding BLOB,                           -- 3072-byte Float32 Little-Endian Blob (<f4)
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- 4. High-Performance B-Tree Indices
CREATE INDEX IF NOT EXISTS idx_chunks_ordering ON prepared_chunks (book_id, page_id);
CREATE INDEX IF NOT EXISTS idx_chunks_section ON prepared_chunks (book_id, section_id);
CREATE INDEX IF NOT EXISTS idx_chunks_book_order ON prepared_chunks (book_id, chunk_order);
CREATE INDEX IF NOT EXISTS idx_sections_book ON sections (book_id, section_level);

-- 5. High-Precision SQLite FTS5 Virtual Table
CREATE VIRTUAL TABLE IF NOT EXISTS prepared_chunks_fts USING fts5 (
    salient_roots_text,
    book_name UNINDEXED,
    section_title UNINDEXED,
    content='prepared_chunks',
    content_rowid='chunk_id',
    tokenize="unicode61 remove_diacritics 0"
);
"""

def init_db_schema(conn):
    """Initializes the complete database schema and indexes."""
    cur = conn.cursor()
    cur.executescript(SCHEMA_DDL)
    conn.commit()

def rebuild_fts_index(conn):
    """Rebuilds the FTS5 index from the content table in a single bulk pass."""
    cur = conn.cursor()
    cur.execute("INSERT INTO prepared_chunks_fts(prepared_chunks_fts) VALUES('rebuild')")
    conn.commit()

def finalize_db(conn):
    """
    Hardens the database file for read-only Docker mounting:
    1. Truncates and merges the WAL into the main database file.
    2. Sets journal_mode to DELETE (safe for immutable read-only mounts).
    3. Runs SQLite query optimizer.
    """
    cur = conn.cursor()
    cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    cur.execute("PRAGMA journal_mode = DELETE;")
    cur.execute("PRAGMA optimize;")
    conn.commit()
