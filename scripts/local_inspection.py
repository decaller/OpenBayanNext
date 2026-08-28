import os
import json
import sqlite3
import pandas as pd
import pyarrow.parquet as pq

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "samples"))

def header(title):
    print("\n" + "="*80)
    print(f"📖 {title}")
    print("="*80)

# 1. AuthenticIlm Books Inspection
header("1. AuthenticIlm Canonical Books (TOC & Page Anatomy)")
books = [
    ("Al-Majmu' (Fiqh Shafi'i)", "16__الفقه-الشافعي/1618__المجموع-شرح-المهذب-ط-المنيرية"),
    ("Bidayat al-Mujtahid (Fiqh Maliki/Muqaran)", "15__الفقه-المالكي/5841__بداية-المجتهد-ونهاية-المقتصد"),
    ("Tafsir Ibn Kathir (Tafsir)", "03__التفسير/6094__تفسير-ابن-كثير-ط-العلمية"),
]

for bname, brel in books:
    bdir = os.path.join(SAMPLE_DIR, "AuthenticIlm_Shamela4_Full_DB", brel)
    print(f"\n▶ Book: {bname}")
    meta_p = os.path.join(bdir, "book_metadata.json")
    if os.path.exists(meta_p):
        with open(meta_p, "r", encoding="utf-8") as f:
            m = json.load(f)
            print(f"   • Book ID: {m.get('book_id')}, Title: {m.get('title_ar')}, Author: {m.get('main_author_name_ar')} (d. {m.get('main_author_death_hijri')} AH)")
            
    toc_p = os.path.join(bdir, "toc.jsonl")
    if os.path.exists(toc_p):
        with open(toc_p, "r", encoding="utf-8") as f:
            tocs = [json.loads(line) for i, line in enumerate(f) if i < 3]
            print(f"   • TOC Nodes (Sample {len(tocs)}):")
            for t in tocs:
                print(f"     - [title_id={t.get('title_id')}, page_id={t.get('page_id')}, parent={t.get('parent_id')}] : {t.get('title_text')}")
                
    pages_p = os.path.join(bdir, "pages.jsonl")
    if os.path.exists(pages_p):
        with open(pages_p, "r", encoding="utf-8") as f:
            p1 = json.loads(f.readline())
            print(f"   • Page 1: page_id={p1.get('page_id')}, vol={p1.get('part')}, page_num={p1.get('page_num')}")
            snippet = p1.get('body', '')[:120].replace('\r', ' ').replace('\n', ' ')
            print(f"     Text snippet: \"{snippet}...\"")
            print(f"     Footnotes: {p1.get('footnotes')}")

# 2. Evaluation QGen Triples
header("2. Synthetic Question-Context-Answer Triples (ohsn/shamela_Qgen)")
for qpath_rel in [
    "ohsn_shamela_Qgen_2000samples/shamela_q_chunk_00_0_500000.parquet",
    "ohsn_qgen/shamela_Qgen_2000samples2/shamela_q_chunk_00_0_500000.parquet"
]:
    qp = os.path.join(SAMPLE_DIR, qpath_rel)
    if os.path.exists(qp):
        t = pq.read_table(qp)
        df = t.to_pandas().head(2)
        print(f"\n▶ File: {qpath_rel} (Total Rows: {len(t)})")
        print(f"   Columns: {t.schema.names}")
        for i, row in df.iterrows():
            print(f"   • QA Pair #{i+1}:")
            for c in df.columns:
                val = str(row[c]).replace('\r', ' ').replace('\n', ' ')
                print(f"     - {c}: {val[:110]}...")

# 3. Dialectical Subsets
header("3. Dialectical Thematic Subsets (MathematicianNLPer)")
for sub in ["shamela_subset_wahhabite", "shamela_subset_not_wahhabite"]:
    sp = os.path.join(SAMPLE_DIR, "MathematicianNLPer", sub, "data", "train-00000-of-00001.parquet")
    if os.path.exists(sp):
        t = pq.read_table(sp)
        df = t.to_pandas().head(1)
        print(f"\n▶ Subset: {sub} ({len(t)} rows)")
        print(f"   Columns: {t.schema.names}")
        for c in df.columns:
            val = str(df[c].iloc[0]).replace('\r', ' ').replace('\n', ' ')
            print(f"   - {c}: {val[:100]}...")

# 4. MoMonir Master Metadata
header("4. Master Bibliographic Metadata (MoMonir/Shamela_Books_info)")
csv_p = os.path.join(SAMPLE_DIR, "MoMonir_Shamela_Books_info", "shamela_books_info.csv")
if os.path.exists(csv_p):
    df_info = pd.read_csv(csv_p)
    print(f"Total Books Cataloged: {len(df_info)}")
    print("Categories Breakdown (Top 8):")
    print(df_info["category"].value_counts().head(8).to_string())
