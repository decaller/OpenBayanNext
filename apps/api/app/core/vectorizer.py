import os
import time
from typing import List, Optional
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from huggingface_hub import hf_hub_download

class E5Vectorizer:
    """
    High-performance CPU E5 Vectorizer using pure ONNX Runtime and HuggingFace Tokenizers.
    Model: Xenova/multilingual-e5-base (768 dimensions, ONNX Quantized).
    Enforces strict 'query: <text>' asymmetric prefixing and L2 unit-norm vectors.
    """
    def __init__(self, model_id: str = "Xenova/multilingual-e5-base"):
        self.model_id = model_id
        self._tokenizer: Optional[Tokenizer] = None
        self._session: Optional[ort.InferenceSession] = None
        self._is_warmed_up: bool = False

    def _ensure_loaded(self):
        if self._session is None or self._tokenizer is None:
            # Download or load cached tokenizer & quantized ONNX model
            tok_path = hf_hub_download(repo_id=self.model_id, filename="tokenizer.json")
            onnx_path = hf_hub_download(repo_id=self.model_id, filename="onnx/model_quantized.onnx")

            self._tokenizer = Tokenizer.from_file(tok_path)
            self._tokenizer.enable_truncation(max_length=512)
            # Do NOT use fixed 512-length padding; dynamic length makes CPU inference 40x faster (< 5ms)

            # CPU Inference Session with optimized thread count
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = min(os.cpu_count() or 4, 8)
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self._session = ort.InferenceSession(
                onnx_path, 
                sess_options=sess_options, 
                providers=["CPUExecutionProvider"]
            )

    def warmup(self):
        """Pre-warms ONNX session and loads weights into memory during FastAPI startup."""
        if self._is_warmed_up:
            return
        t0 = time.perf_counter()
        self._ensure_loaded()
        _ = self.embed_query("صلاة")
        self._is_warmed_up = True
        t1 = time.perf_counter()
        print(f"✓ E5 Vectorizer pre-warmed in {(t1-t0)*1000:.2f} ms ({self.model_id})")

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string with mandatory 'query: ' prefix.
        Returns a normalized 768-dim float32 NumPy array in < 5 ms on CPU.
        """
        self._ensure_loaded()
        formatted_query = f"query: {query.strip()}"
        enc = self._tokenizer.encode(formatted_query)

        input_ids = np.array([enc.ids], dtype=np.int64)
        attention_mask = np.array([enc.attention_mask], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids)

        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        input_names = [inp.name for inp in self._session.get_inputs()]
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = token_type_ids

        out = self._session.run(None, inputs)
        last_hidden = out[0] # (1, seq_len, 768)

        # Mean pooling with attention mask
        mask_expanded = np.expand_dims(attention_mask, -1)
        sum_embeddings = np.sum(last_hidden * mask_expanded, axis=1)
        sum_mask = np.clip(mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        embedding = (sum_embeddings / sum_mask)[0].astype("<f4")

        # L2 Normalization
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

vectorizer = E5Vectorizer()
