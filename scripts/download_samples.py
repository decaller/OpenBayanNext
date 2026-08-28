import os
import json
import requests
import sys

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "samples"))
os.makedirs(SAMPLE_DIR, exist_ok=True)

TARGET_REPOS = [
    {"repo_id": "AuthenticIlm/Shamela4_Full_DB", "type": "dataset"},
    {"repo_id": "Kandil7/Athar-Shamela4", "type": "dataset"},
    {"repo_id": "Maktabati/shamela-vectors", "type": "dataset"},
    {"repo_id": "MoMonir/Shamela_Books_info", "type": "dataset"},
    {"repo_id": "MoMonir/shamela_books_text_full", "type": "dataset"},
    {"repo_id": "ohsn/shamela_Qgen_2000samples", "type": "dataset"},
    {"repo_id": "Saheerakp/golden-shamela", "type": "dataset"},
]

def list_and_sample(repo_id):
    print(f"\n==========================================")
    print(f"🔍 Inspecting: {repo_id}")
    print(f"==========================================")
    url = f"https://huggingface.co/api/datasets/{repo_id}"
    headers = {"User-Agent": "OpenBayan-Diagnostic/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"⚠️ Failed to get metadata ({r.status_code}): {r.text[:200]}")
            return
        data = r.json()
        siblings = data.get("siblings", [])
        print(f"Total files listed: {len(siblings)}")
        
        # Print first 10 files
        for f in siblings[:10]:
            print(f"  - {f.get('rfilename')}")
        if len(siblings) > 10:
            print(f"  ... and {len(siblings) - 10} more files.")
            
        # Target specific sample files to download
        repo_clean_name = repo_id.replace("/", "_")
        dest_dir = os.path.join(SAMPLE_DIR, repo_clean_name)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Pick 1-2 small files (e.g. metadata, json, jsonl, parquet, small samples)
        candidates = []
        for f in siblings:
            fname = f.get('rfilename', '')
            if fname.endswith(('.json', '.jsonl', '.parquet', '.csv', '.md', '.txt')):
                candidates.append(fname)
                
        print(f"\nDownloading up to 2 sample files for {repo_id}...")
        downloaded = 0
        for fname in candidates:
            if downloaded >= 2:
                break
            # Skip massive files > 50MB by checking raw url stream
            file_url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/{fname}"
            local_path = os.path.join(dest_dir, os.path.basename(fname))
            if os.path.exists(local_path):
                print(f"  ✓ Already exists: {local_path}")
                downloaded += 1
                continue
                
            print(f"  ⬇️ Downloading {fname} ...")
            try:
                with requests.get(file_url, headers=headers, stream=True, timeout=20) as stream_resp:
                    if stream_resp.status_code == 200:
                        content_len = stream_resp.headers.get('content-length')
                        if content_len and int(content_len) > 50 * 1024 * 1024:
                            print(f"    ⏩ Skipping large file ({int(content_len)/(1024*1024):.1f} MB): {fname}")
                            continue
                        
                        with open(local_path, 'wb') as out_f:
                            bytes_written = 0
                            for chunk in stream_resp.iter_content(chunk_size=65536):
                                if chunk:
                                    out_f.write(chunk)
                                    bytes_written += len(chunk)
                                    # Cap sample download at 15MB
                                    if bytes_written > 15 * 1024 * 1024:
                                        print(f"    ✂️ Truncated sample at 15MB: {fname}")
                                        break
                        print(f"  ✓ Saved to {local_path} ({bytes_written} bytes)")
                        downloaded += 1
                    else:
                        print(f"    ⚠️ HTTP {stream_resp.status_code} for {fname}")
            except Exception as e:
                print(f"    ❌ Error downloading {fname}: {e}")
                
    except Exception as e:
        print(f"❌ Error connecting to HF for {repo_id}: {e}")

if __name__ == "__main__":
    for target in TARGET_REPOS:
        list_and_sample(target["repo_id"])
