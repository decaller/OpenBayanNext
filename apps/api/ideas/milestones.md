Using **`AuthenticIlm/Shamela4_Full_DB`** for pre-built Table of Contents (TOC) trees, **`Maktabati/shamela-vectors`** for pre-computed dense embeddings, and **`ohsn/shamela_Qgen`** for evaluation removes the need for regex-based structural parsing and GPU embedding generation.

The MVP focuses on a controlled 5,000–10,000 passage vertical slice (e.g., *Iḥyāʾ ʿUlūm al-Dīn*, *Bidāyat al-Mujtahid*, and *Al-Majmūʿ*).

---

### Revised MVP Milestone Roadmap

| Milestone | Core Deliverable | Primary Dataset & Tools | Validation Gate |
| --- | --- | --- | --- |
| **M1: Hierarchical Ingestion & Vector Loading** | Ingest `pages.jsonl` + `toc.jsonl`, join pre-computed vectors, extract roots, build Turso DB. | `AuthenticIlm`, `Maktabati/vectors`, Prefect, Turso/libSQL | 10k passages indexed with Tantivy BM25 + Vectors in $<2\text{ mins}$. |
| **M2: Hybrid Retrieval & Bitset Jaccard Core** | Sibling merger, elastic boundary context ($N \pm 1$), SIMD Jaccard clustering. | FastAPI, NumPy SIMD, `libsql-client` | Search + clustering execution under $5\text{ ms}$ for 50 candidates. |
| **M3: Synthesis & Autonomous Agent MCP** | SSE token streaming with footnote anchors (`[^ref1]`), MCP agent search tool. | LiteLLM / vLLM, Pydantic, MCP SDK | Citations link 1:1 to database `chunk_id` and permalinks. |
| **M4: Astro SSR & Interactive Islands** | 0-JS `/p/:id` permalinks, DaisyUI/React search islands, 3-tier depth toggles. | Astro SSR, React, Nanostores, DaisyUI | Raw HTML payload $< 2\text{ KB}$, 0 CLS on Arabic typography. |
| **M5: RAG Evaluation & Gateway Deploy** | End-to-end benchmark against synthetic QA pairs, container stack behind Zoraxy. | `ohsn/shamela_Qgen_2000samples`, Zoraxy, Docker | Recall@5 $\ge 85\%$ on test questions; 100% crawler pass. |

---

### Milestone Breakdown

**Milestone 1: Hierarchical Ingestion & Vector Loading**

* **TOC-Guided Slicing:** Stream target books from `AuthenticIlm/Shamela4_Full_DB`. Parse `toc.jsonl` directly to assign explicit `section_id`, `section_level` (*Kitāb/Bāb/Faṣl*), and breadcrumbs without text regex heuristics.
* **Footnote Isolation:** Store body text in `raw_text` and keep original footnotes in a dedicated column to prevent search score corruption.
* **Vector Ingestion:** Join passage identifiers directly against `Maktabati/shamela-vectors` Parquet files to populate the `embedding` column.
* **Linguistic Indexing:** Run Farasa to populate `salient_roots_text`, calculate 512-byte MinHash signatures via `datasketch`, and commit batches to Turso with Tantivy FTS enabled.

**Milestone 2: Hybrid Retrieval & Context Engine**

* **Dual-Path Search:** Implement `/api/v1/search` combining Tantivy BM25 root matching and Vector KNN distance scoring.
* **Contiguous Sibling Merger:** Automatically fuse consecutive hits from the same section into unified reading passages.
* **Boundary-Aware Expansion:** Implement `/api/v1/chunks/{id}/surrounding` utilizing the pre-indexed `toc.jsonl` boundaries to resolve Level-2 context ($N-1 \leftrightarrow N+1$) without spilling across unrelated chapters.
* **SIMD Clustering:** Execute NumPy pairwise Jaccard matrix clustering over candidate MinHash byte blobs in $< 1\text{ ms}$.

**Milestone 3: Grounded Synthesis & AI Agent Protocols**

* **SSE Stream Router:** Build `GET /api/v1/synthesis/stream` emitting `meta`, `token`, and `citations` frames.
* **Citation Grounding Contract:** Constrain LLM synthesis prompts to the clustered candidate text, requiring exact footnote anchors (`[^ref1]`) tied to `chunk_id`.
* **Agent Tool Spec:** Build `POST /api/v1/agent/tools/search_corpus` conforming to MCP standards, returning structured text, bookend context, and canonical URLs.

**Milestone 4: Astro SSR & Reactive Island Workspace**

* **Crawlable Permalinks:** Build `src/pages/p/[id].astro` rendering clean semantic HTML and Schema.org `ScholarlyArticle` JSON-LD with zero client JavaScript.
* **Workspace Islands:** Implement `<SearchBar client:load/>` and `<PassageCard/>` with 3-tier depth toggles:
* *Level 1 (مقتطف):* Compact snippet.
* *Level 2 (سياق):* Sibling context with boundary highlights.
* *Level 3 (مطالعة):* Opens the `<CitationDrawer client:idle/>` for full chapter reading.


* **State Coordination:** Bind DaisyUI drawer toggles directly to Nanostores (`$isDrawerOpen`, `$activeCitation`).

**Milestone 5: Benchmark Evaluation, Gateway & Deployment**

* **Automated Retrieval Audit:** Run a test harness using the 2,000 question-context pairs in `ohsn/shamela_Qgen_2000samples` to benchmark Recall@K and Mean Reciprocal Rank (MRR).
* **Gateway Orchestration:** Configure `docker-compose.yml` deploying Zoraxy, Astro SSR (Node adapter), and the FastAPI container with read-only NVMe mounts.
* **Bot Verification:** Audit response payloads against `GPTBot`, `ClaudeBot`, and `curl` to verify instantaneous first-byte text indexing.