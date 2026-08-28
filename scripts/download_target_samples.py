import os
import json
import requests

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "samples"))

# 1. Download specific pages.jsonl and toc.jsonl from AuthenticIlm
target_book_files = [
    ("AuthenticIlm/Shamela4_Full_DB", "01__العقيدة/1009__شرح-العقيدة-الطحاوية-عبد-العزيز-الراجحي/pages.jsonl", "AuthenticIlm_Shamela4_Full_DB/pages.jsonl"),
    ("AuthenticIlm/Shamela4_Full_DB", "01__العقيدة/1009__شرح-العقيدة-الطحاوية-عبد-العزيز-الراجحي/toc.jsonl", "AuthenticIlm_Shamela4_Full_DB/toc.jsonl"),
    ("Maktabati/shamela-vectors", "index_shamela_v1.py", "Maktabati_shamela-vectors/index_shamela_v1.py"),
    ("Saheerakp/golden-shamela", "books/0/10.db", "Saheerakp_golden-shamela/10.db"),
]

headers = {"User-Agent": "OpenBayan-Diagnostic/1.0"}

for repo_id, rfile, local_rel in target_book_files:
    local_path = os.path.join(SAMPLE_DIR, local_rel)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if os.path.exists(local_path):
        print(f"✓ Already exists: {local_path}")
        continue
    url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/{rfile}"
    print(f"⬇️ Downloading {rfile} -> {local_path} ...")
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                print(f"✓ Downloaded {os.path.getsize(local_path)} bytes")
            else:
                print(f"⚠️ HTTP {r.status_code} for {rfile}")
    except Exception as e:
        print(f"❌ Error: {e}")
