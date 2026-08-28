import os
import json
import duckdb

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "samples"))

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

def print_header(title):
    print("\n" + "="*80)
    print(f"📊 {title}")
    print("="*80)

# 1. Maktabati Vectors Parquet via DuckDB HTTPFS Range Query
print_header("1. Maktabati / shamela-vectors Schema & Sample (Streamed via HTTPFS)")
try:
    vec_url = "https://huggingface.co/datasets/Maktabati/shamela-vectors/resolve/main/shamela-00000.parquet"
    res = con.execute(f"SELECT * FROM '{vec_url}' LIMIT 2").df()
    print("Columns in shamela-00000.parquet:", res.columns.tolist())
    for i, row in res.iterrows():
        print(f"\n--- Row {i+1} ---")
        for col in res.columns:
            val = row[col]
            if col == "vector":
                print(f"  vector: list of {len(val)} floats (dim={len(val)}), sample: {val[:3]}...")
            elif isinstance(val, str) and len(val) > 100:
                print(f"  {col}: {val[:100]}...")
            else:
                print(f"  {col}: {val}")
except Exception as e:
    print("DuckDB remote query note:", e)

# 2. AuthenticIlm Pages & TOC
print_header("2. AuthenticIlm (Pages & TOC Integration)")
toc_path = os.path.join(SAMPLE_DIR, "AuthenticIlm_Shamela4_Full_DB", "16__الفقه-الشافعي", "1618__المجموع-شرح-المهذب-ط-المنيرية", "toc.jsonl")
pages_path = os.path.join(SAMPLE_DIR, "AuthenticIlm_Shamela4_Full_DB", "16__الفقه-الشافعي", "1618__المجموع-شرح-المهذب-ط-المنيرية", "pages.jsonl")

if os.path.exists(toc_path):
    print("Al-Majmu' TOC (First 3 entries):")
    with open(toc_path, "r", encoding="utf-8") as f:
        for i, l in enumerate(f):
            if i >= 3: break
            print(f"  {l.strip()}")

if os.path.exists(pages_path):
    print("\nAl-Majmu' Pages (First entry):")
    with open(pages_path, "r", encoding="utf-8") as f:
        p1 = json.loads(f.readline())
        for k, v in p1.items():
            if k == "body" and isinstance(v, str):
                print(f"  {k}: {v[:120]}...")
            else:
                print(f"  {k}: {v}")

# 3. ohsn / shamela_Qgen Triples
print_header("3. ohsn / shamela_Qgen_2000samples Evaluation Triples")
qgen_path = os.path.join(SAMPLE_DIR, "ohsn_shamela_Qgen_2000samples", "shamela_q_chunk_00_0_500000.parquet")
if os.path.exists(qgen_path):
    try:
        q_df = con.execute(f"SELECT * FROM '{qgen_path}' LIMIT 2").df()
        print("Columns in QGen:", q_df.columns.tolist())
        for i, row in q_df.iterrows():
            print(f"\n--- QA Sample {i+1} ---")
            for col in q_df.columns:
                val = str(row[col])
                print(f"  {col}: {val[:120]}...")
    except Exception as e:
        print("QGen local read note:", e)

# 4. MathematicianNLPer Thematic Subsets
print_header("4. MathematicianNLPer Thematic Subsets")
for sub in ["shamela_subset_wahhabite", "shamela_subset_not_wahhabite"]:
    p = os.path.join(SAMPLE_DIR, "MathematicianNLPer", sub, "data", "train-00000-of-00001.parquet")
    if os.path.exists(p):
        t_df = con.execute(f"SELECT * FROM '{p}' LIMIT 1").df()
        print(f"\nSubset '{sub}' Columns: {t_df.columns.tolist()}")
        for col in t_df.columns:
            print(f"  {col}: {str(t_df[col].iloc[0])[:100]}...")
