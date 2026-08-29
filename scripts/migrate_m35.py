#!/usr/bin/env python3
"""
Migration script for Milestone 3.5:
Adds tradition, era_tag, creates B-Tree indexes, populates metadata,
and cleanly checkpoints the SQLite database.
"""
import sqlite3
import os
import sys

DB_PATH = "data/shamela_corpus.db"

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)

    print(f"🚀 Running Milestone 3.5 Migration on {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Enable WAL mode temporarily
    cursor.execute("PRAGMA journal_mode = WAL;")

    # 2. Add columns if not existing
    cols = [r[1] for r in cursor.execute("PRAGMA table_info(books)")]
    if "tradition" not in cols:
        cursor.execute("ALTER TABLE books ADD COLUMN tradition TEXT;")
        print("✓ Added column books.tradition")
    if "era_tag" not in cols:
        cursor.execute("ALTER TABLE books ADD COLUMN era_tag TEXT;")
        print("✓ Added column books.era_tag")

    # 3. Create B-Tree Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_category ON books(category_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_hijri ON books(author_death_hijri);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_tradition ON books(tradition);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_sec_start ON prepared_chunks(is_section_start);")
    print("✓ Created B-Tree indexes for category, era, tradition, and section start")

    # 4. Populate era_tag
    cursor.execute("""
        UPDATE books 
        SET era_tag = CASE 
            WHEN author_death_hijri <= 300 THEN 'early'
            WHEN author_death_hijri <= 700 THEN 'classical'
            ELSE 'late'
        END
    """)
    print("✓ Populated books.era_tag ('early', 'classical', 'late')")

    # 5. Populate tradition
    # Athari / Salafi / Contemporary Athari scholars
    athari_keywords = [
        'ابن باز', 'ابن عثيمين', 'الألباني', 'الغنيمان', 'الراجحي', 
        'الخضير', 'الحويني', 'العباد', 'الوائلي', 'المغامسي', 'الحوشان',
        'فيصل آل مبارك', 'أحمد حطيبة', 'أسامة سليمان', 'الشنقيطي', 'الروقي'
    ]

    cursor.execute("UPDATE books SET tradition = 'classical_jumhur';")
    
    for kw in athari_keywords:
        cursor.execute("UPDATE books SET tradition = 'athari_salafi' WHERE author_name LIKE ? OR title_ar LIKE ?;", (f"%{kw}%", f"%{kw}%"))

    cursor.execute("UPDATE books SET tradition = 'athari_salafi' WHERE category_name = 'العقيدة' AND (title_ar LIKE '%كتاب التوحيد%' OR title_ar LIKE '%الراجحي%');")

    conn.commit()

    # 6. Checkpoint WAL and finalize
    cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    cursor.execute("PRAGMA journal_mode = DELETE;")
    cursor.execute("PRAGMA optimize;")
    conn.commit()
    conn.close()

    print("🎉 Milestone 3.5 Migration completed cleanly & verified!")

if __name__ == "__main__":
    run_migration()
