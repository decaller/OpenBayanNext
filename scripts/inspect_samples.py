import os
import json
import sqlite3
import pandas as pd

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "samples"))

print("================================================================")
print("1. AuthenticIlm/Shamela4_Full_DB Sample Analysis")
print("================================================================")

# Metadata
meta_path = os.path.join(SAMPLE_DIR, "AuthenticIlm_Shamela4_Full_DB", "book_metadata.json")
if os.path.exists(meta_path):
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        print("Book Metadata:")
        print(json.dumps(meta, ensure_ascii=False, indent=2))

# TOC
toc_path = os.path.join(SAMPLE_DIR, "AuthenticIlm_Shamela4_Full_DB", "toc.jsonl")
if os.path.exists(toc_path):
    print("\nTOC Sample (First 3 entries):")
    with open(toc_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            print(f"  Line {i+1}: {line.strip()}")

# Pages
pages_path = os.path.join(SAMPLE_DIR, "AuthenticIlm_Shamela4_Full_DB", "pages.jsonl")
if os.path.exists(pages_path):
    print("\nPages Sample (First 2 entries):")
    with open(pages_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 2:
                break
            page_data = json.loads(line)
            # truncate long text
            if "body" in page_data:
                page_data["body_snippet"] = page_data["body"][:150] + "..."
                del page_data["body"]
            print(f"  Page {i+1}: {json.dumps(page_data, ensure_ascii=False, indent=2)}")

print("\n================================================================")
print("2. ohsn/shamela_Qgen_2000samples Parquet Analysis")
print("================================================================")
qgen_path = os.path.join(SAMPLE_DIR, "ohsn_shamela_Qgen_2000samples", "shamela_q_chunk_00_0_500000.parquet")
if os.path.exists(qgen_path):
    try:
        import pyarrow.parquet as pq
        table = pq.read_table(qgen_path)
        print("QGen Schema:", table.schema)
        df = table.to_pandas().head(2)
        print("\nQGen First 2 Rows:")
        for idx, row in df.iterrows():
            print(f"  Row {idx}:")
            for col in df.columns:
                val = str(row[col])
                if len(val) > 100:
                    val = val[:100] + "..."
                print(f"    {col}: {val}")
    except Exception as e:
        print("PyArrow not installed, reading with basic inspector if possible:", e)

print("\n================================================================")
print("3. Saheerakp/golden-shamela SQLite Schema")
print("================================================================")
db_path = os.path.join(SAMPLE_DIR, "Saheerakp_golden-shamela", "10.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables in 10.db:")
    for t_name, t_sql in tables:
        print(f"  Table: {t_name}")
        print(f"    SQL: {t_sql}")
        cur.execute(f"SELECT * FROM {t_name} LIMIT 1")
        row = cur.fetchone()
        print(f"    Sample row: {row}")
    conn.close()

print("\n================================================================")
print("4. MoMonir/Shamela_Books_info CSV Analysis")
print("================================================================")
csv_path = os.path.join(SAMPLE_DIR, "MoMonir_Shamela_Books_info", "shamela_books_info.csv")
if os.path.exists(csv_path):
    df_info = pd.read_csv(csv_path, nrows=3)
    print("Columns:", df_info.columns.tolist())
    print("Sample Rows:\n", df_info.to_string())
