import os
import sys
import time
import sqlite3
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from huggingface_hub import hf_hub_download

DB_PATH = "data/shamela_corpus.db"
MODEL_ID = "Xenova/multilingual-e5-base"
BATCH_SIZE = 64
NUM_WORKERS = min(8, os.cpu_count() or 4)
COMMIT_INTERVAL = 2048
MAX_TOKENS = 192

# Global worker variables
_worker_tokenizer = None
_worker_session = None
_worker_input_names = None

def init_worker():
    """Initializes isolated ONNX session per worker process."""
    global _worker_tokenizer, _worker_session, _worker_input_names
    tok_path = hf_hub_download(repo_id=MODEL_ID, filename="tokenizer.json")
    onnx_path = hf_hub_download(repo_id=MODEL_ID, filename="onnx/model_quantized.onnx")

    _worker_tokenizer = Tokenizer.from_file(tok_path)
    _worker_tokenizer.enable_truncation(max_length=MAX_TOKENS)
    _worker_tokenizer.enable_padding(length=None)

    sess_options = ort.SessionOptions()
    sess_options.intra_op_num_threads = 2
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    _worker_session = ort.InferenceSession(
        onnx_path,
        sess_options=sess_options,
        providers=["CPUExecutionProvider"]
    )
    _worker_input_names = [inp.name for inp in _worker_session.get_inputs()]

def process_chunk_batch(batch: List[Tuple[int, str]]) -> List[Tuple[bytes, int]]:
    """Encodes a batch of (chunk_id, raw_text) into (embedding_blob, chunk_id)."""
    global _worker_tokenizer, _worker_session, _worker_input_names

    chunk_ids = [r[0] for r in batch]
    formatted_texts = [f"passage: {r[1].strip()[:1000]}" for r in batch]

    encs = _worker_tokenizer.encode_batch(formatted_texts)
    input_ids = np.array([e.ids for e in encs], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encs], dtype=np.int64)

    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask
    }
    if "token_type_ids" in _worker_input_names:
        inputs["token_type_ids"] = np.zeros_like(input_ids)

    out = _worker_session.run(None, inputs)
    last_hidden = out[0]

    # Mean pooling
    mask_expanded = np.expand_dims(attention_mask, -1)
    sum_embeddings = np.sum(last_hidden * mask_expanded, axis=1)
    sum_mask = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    embeddings = sum_embeddings / sum_mask

    # L2 Normalization
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = (embeddings / norms).astype("<f4")

    return list(zip([vec.tobytes() for vec in normalized], chunk_ids))

def run_embedding_pipeline():
    print("=" * 70)
    print(f"🚀 OPENBAYAN: MULTI-CORE CORPUS VECTOR EMBEDDING PIPELINE ({NUM_WORKERS} WORKERS)")
    print("=" * 70)

    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file {DB_PATH} not found.")
        sys.exit(1)

    # 1. Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = -128000;")
    cur = conn.cursor()

    # 2. Fetch unembedded chunks
    print("\n[1/3] Scanning database for un-embedded chunks...")
    cur.execute("SELECT chunk_id, raw_text FROM prepared_chunks WHERE embedding IS NULL ORDER BY chunk_id ASC")
    rows = cur.fetchall()
    total_unembedded = len(rows)

    total_chunks = cur.execute("SELECT COUNT(*) FROM prepared_chunks").fetchone()[0]
    already_embedded = total_chunks - total_unembedded

    print(f"  • Total corpus chunks: {total_chunks:,}")
    print(f"  • Already embedded:    {already_embedded:,} ({(already_embedded/total_chunks)*100:.1f}%)")
    print(f"  • Remaining to embed:  {total_unembedded:,} ({(total_unembedded/total_chunks)*100:.1f}%)")

    if total_unembedded == 0:
        print("\n✓ 100% of corpus is already vectorized! No work required.")
        conn.close()
        return

    # 3. Create batch chunks
    batches = [rows[i : i + BATCH_SIZE] for i in range(0, total_unembedded, BATCH_SIZE)]
    print(f"\n[2/3] Processing {len(batches):,} batches across {NUM_WORKERS} worker processes...")
    
    start_time = time.perf_counter()
    processed_count = 0
    update_buffer = []

    with ProcessPoolExecutor(max_workers=NUM_WORKERS, initializer=init_worker) as executor:
        for result_batch in executor.map(process_chunk_batch, batches, chunksize=4):
            update_buffer.extend(result_batch)
            processed_count += len(result_batch)

            if len(update_buffer) >= COMMIT_INTERVAL:
                cur.executemany(
                    "UPDATE prepared_chunks SET embedding = ? WHERE chunk_id = ?",
                    update_buffer
                )
                conn.commit()
                update_buffer.clear()

                elapsed = time.perf_counter() - start_time
                rate = processed_count / elapsed
                eta_sec = (total_unembedded - processed_count) / rate if rate > 0 else 0
                current_total = already_embedded + processed_count
                print(
                    f"  • Progress: {processed_count:,}/{total_unembedded:,} "
                    f"({(current_total / total_chunks) * 100:.1f}% Total) | "
                    f"Speed: {rate:.1f} chunks/s | ETA: {eta_sec / 60:.1f}m"
                )

    # Final commit
    if update_buffer:
        cur.executemany(
            "UPDATE prepared_chunks SET embedding = ? WHERE chunk_id = ?",
            update_buffer
        )
        conn.commit()

    total_time = time.perf_counter() - start_time
    print(f"\n✓ Successfully embedded {total_unembedded:,} chunks in {total_time / 60:.2f} minutes ({total_unembedded/total_time:.1f} chunks/s).")

    # 4. Finalize database checkpoint
    print("\n[3/3] Checkpointing database...")
    cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    cur.execute("PRAGMA optimize;")
    conn.close()
    print("✓ SQLite database checkpointed and finalized successfully.")

if __name__ == "__main__":
    run_embedding_pipeline()
