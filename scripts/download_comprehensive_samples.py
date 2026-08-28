import os
import json
import requests

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "samples"))
os.makedirs(SAMPLE_DIR, exist_ok=True)

headers = {"User-Agent": "OpenBayan-Diagnostic/1.0"}

def get_repo_files(repo_id):
    url = f"https://huggingface.co/api/datasets/{repo_id}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return [f.get("rfilename") for f in r.json().get("siblings", [])]
    except Exception as e:
        print(f"Error fetching file list for {repo_id}: {e}")
    return []

def download_file(repo_id, rfile, local_rel_path, max_bytes=50*1024*1024):
    local_path = os.path.join(SAMPLE_DIR, local_rel_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if os.path.exists(local_path):
        print(f"  ✓ Already exists: {local_rel_path} ({os.path.getsize(local_path)} bytes)")
        return
    url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/{rfile}"
    print(f"  ⬇️ Downloading {rfile} -> {local_rel_path} ...")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            if r.status_code == 200:
                content_len = r.headers.get("content-length")
                if content_len:
                    size_mb = int(content_len) / (1024*1024)
                    print(f"     Size: {size_mb:.2f} MB")
                with open(local_path, "wb") as f:
                    written = 0
                    for chunk in r.iter_content(chunk_size=131072):
                        if chunk:
                            f.write(chunk)
                            written += len(chunk)
                            if written >= max_bytes:
                                print(f"     ✂️ Capped at {max_bytes/(1024*1024):.1f} MB")
                                break
                print(f"  ✓ Saved {local_rel_path} ({written} bytes)")
            else:
                print(f"  ⚠️ HTTP {r.status_code} for {rfile}")
    except Exception as e:
        print(f"  ❌ Error downloading {rfile}: {e}")

def main():
    # 1. Kandil7/Athar-Shamela4 _meta/ files
    print("\n--- 1. Kandil7/Athar-Shamela4 Meta Cross-Refs ---")
    athar_files = get_repo_files("Kandil7/Athar-Shamela4")
    meta_files = [f for f in athar_files if f.startswith("_meta/") or "_meta" in f or "root" in f or "isnad" in f or "narrator" in f]
    print(f"Found {len(meta_files)} meta files in Athar-Shamela4: {meta_files[:10]}")
    for mf in meta_files[:5]:
        download_file("Kandil7/Athar-Shamela4", mf, f"Kandil7_Athar-Shamela4/{mf}")

    # 2. Maktabati/shamela-vectors shamela-00000.parquet
    print("\n--- 2. Maktabati/shamela-vectors Parquet Partition ---")
    download_file("Maktabati/shamela-vectors", "shamela-00000.parquet", "Maktabati_shamela-vectors/shamela-00000.parquet", max_bytes=30*1024*1024)

    # 3. Canonical Books in AuthenticIlm/Shamela4_Full_DB
    print("\n--- 3. Canonical Books in AuthenticIlm (Hadith, Fiqh, Tafsir) ---")
    auth_files = get_repo_files("AuthenticIlm/Shamela4_Full_DB")
    
    # Let's search for canonical books like Bukhari, Nawawi, Ibn Kathir
    canonical_patterns = ["صحيح-البخاري", "المجموع-شرح-المهذب", "تفسير-ابن-كثير", "بداية-المجتهد", "رياض-الصالحين"]
    found_books = {}
    for f in auth_files:
        for pat in canonical_patterns:
            if pat in f:
                book_folder = "/".join(f.split("/")[:-1])
                if pat not in found_books:
                    found_books[pat] = []
                found_books[pat].append(f)
                
    for pat, files in found_books.items():
        print(f"Found canonical book '{pat}': {len(files)} files")
        for f in files:
            if f.endswith(("book_metadata.json", "toc.jsonl", "manifest.json")):
                download_file("AuthenticIlm/Shamela4_Full_DB", f, f"AuthenticIlm_Shamela4_Full_DB/{f}")
            elif f.endswith("pages.jsonl"):
                # limit pages.jsonl to 5MB sample
                download_file("AuthenticIlm/Shamela4_Full_DB", f, f"AuthenticIlm_Shamela4_Full_DB/{f}", max_bytes=5*1024*1024)

    # 4. ReligiousLLMs/shamela_all_diacritized_fully
    print("\n--- 4. ReligiousLLMs/shamela_all_diacritized_fully ---")
    diac_files = get_repo_files("ReligiousLLMs/shamela_all_diacritized_fully")
    print(f"Found {len(diac_files)} files in diacritized dataset: {diac_files[:5]}")
    for df in diac_files:
        if df.endswith((".parquet", ".json", ".csv", ".jsonl")):
            download_file("ReligiousLLMs/shamela_all_diacritized_fully", df, f"ReligiousLLMs_diacritized/{df}", max_bytes=10*1024*1024)
            break

    # 5. MathematicianNLPer Subsets (Wahhabite & Not-Wahhabite)
    print("\n--- 5. MathematicianNLPer Subsets ---")
    for sub in ["MathematicianNLPer/shamela_subset_wahhabite", "MathematicianNLPer/shamela_subset_not_wahhabite"]:
        sub_files = get_repo_files(sub)
        sub_name = sub.split("/")[-1]
        print(f"Files in {sub}: {sub_files[:5]}")
        for sf in sub_files:
            if sf.endswith((".parquet", ".csv", ".json", ".jsonl")):
                download_file(sub, sf, f"MathematicianNLPer/{sub_name}/{sf}", max_bytes=10*1024*1024)
                break

    # 6. ohsn/shamela_Qgen_5000samples & 2000samples2
    print("\n--- 6. QGen Evaluation Datasets ---")
    for qgen in ["ohsn/shamela_Qgen_5000samples", "ohsn/shamela_Qgen_2000samples2"]:
        qfiles = get_repo_files(qgen)
        qname = qgen.split("/")[-1]
        print(f"Files in {qgen}: {qfiles[:5]}")
        for qf in qfiles:
            if qf.endswith(".parquet"):
                download_file(qgen, qf, f"ohsn_qgen/{qname}/{qf}", max_bytes=10*1024*1024)
                break

if __name__ == "__main__":
    main()
