# OpenBayan Classical Arabic IR & Synthesis: MVP Milestones Roadmap

Using **`AuthenticIlm/Shamela4_Full_DB`** for pre-built Table of Contents (TOC) trees, **`Maktabati/shamela-vectors`** for pre-computed 768-dim dense embeddings (`intfloat/multilingual-e5-base`), and **`ohsn/shamela_Qgen`** for evaluation removes the need for regex-based structural parsing and GPU embedding generation.

The MVP focuses on a controlled 5,000–10,000 passage vertical slice across canonical reference works (*Al-Majmūʿ Sharḥ al-Muhadhdhab*, *Bidāyat al-Mujtahid*, *Iḥyāʾ ʿUlūm al-Dīn*, *Tafsīr Ibn Kathīr*, and *Ṣaḥīḥ al-Bukhārī*).

---

## 🏗️ Architectural Shifts Post-Sample Inspection

| Pipeline Stage | Previous Spec Assumption | Revised Best Practice (Post-Inspection) | Impact |
| :--- | :--- | :--- | :--- |
| **Ingestion Hierarchy** | Regex `HeadingStackTracker` parsing text | Parse `toc.jsonl` with explicit `parent_id` and `page_id` | **Zero structural guesswork.** Clean *Kitāb $\to$ Bāb $\to$ Faṣl* hierarchy. |
| **Dense Embeddings** | Generate embeddings locally on GPU | Direct Parquet join with `Maktabati/shamela-vectors` (768-dim E5) | **Bypasses GPU compute entirely.** Ingestion finishes in minutes. |
| **Query Embedding** | Mandatory client-side WebGPU (220MB) | Server-side `fastembed` / ONNX on FastAPI with `"query: "` prefix | **Avoids 220MB client download** on mobile; optional client WebGPU later. |
| **Search Engine** | Experimental "Tantivy DDL" in SQLite | Native **SQLite / libSQL FTS5** (`unicode61 remove_diacritics 2`) | **Sub-2ms BM25 ranking** natively in single-file DB without external daemons. |
| **Tokenization Format** | Bare trilateral roots only (`س-ل-م`) | Composite Lemma + Root tokens (`سلم سليم تسليم اسلم`) | **Prevents over-stemming** and legal term confusion in BM25 ranking. |
| **Clustering Engine** | MinHash Jaccard ($J \ge 0.40$) on roots | TOC Hierarchical Grouping + Vector Cosine Clustering | **Semantically coherent groups**; MinHash reserved for quote deduplication. |
| **Quality Gate** | Manual qualitative spot-checking | Automated benchmark harness against `ohsn/shamela_Qgen` | **Objective quantitative metrics** (Recall@K & MRR) before frontend release. |

---

## 🗺️ Revised 5-Stage MVP Roadmap

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    REVISED MVP IMPLEMENTATION STACK                    │
 ├───────────────────────────────────┬────────────────────────────────────┤
 │ M1: Ingestion & Artifact Join     │ M2: Hybrid Engine & Evaluation     │
 │ • Stream AuthenticIlm (TOC+Pages) │ • FastEmbed Server-side Vectorizer │
 │ • Join Maktabati Vectors (768-dim)│ • SQLite FTS5 (Lemma + Roots)      │
 │ • Extract Composite Lemmas+Roots  │ • Automated Qgen Eval (MRR/Recall) │
 ├───────────────────────────────────┼────────────────────────────────────┤
 │ M3: Grounded Synthesis & MCP      │ M4: Astro SSR & DaisyUI Islands    │
 │ • Strict LLM Grounding Contract   │ • Zero-JS Permalinks (`/p/:id`)    │
 │ • Footnote Anchors (`[^ref1]`)    │ • 3-Tier Depth Toggles             │
 │ • Autonomous Agent Tool Spec (MCP)│ • Nanostores Citation Drawer       │
 ├───────────────────────────────────┴────────────────────────────────────┤
 │ M5: Reverse Proxy (Zoraxy) & Production Gateway                        │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Detailed Milestone Deliverables

### Milestone 1: Streamed Ingestion & Artifact Join (Backend / Pipeline)

* **Target Canonical Slice:** Ingest canonical works from `AuthenticIlm/Shamela4_Full_DB` in `data/samples/` (*Al-Majmūʿ*, *Bidāyat al-Mujtahid*, *Iḥyāʾ*, *Tafsīr Ibn Kathīr*, *Ṣaḥīḥ al-Bukhārī*).
* **Page-to-TOC Forward Fill:** Map `toc.jsonl` onto `pages.jsonl` via `page_id` to assign explicit `section_id`, `section_level`, `section_title`, and breadcrumbs to each physical page.
* **Footnote Isolation:** Store body text in `raw_text` and keep original footnotes in a dedicated `footnotes` column to prevent BM25 score corruption.
* **Vector Join:** Join `(book_id, page_id)` directly against `Maktabati/shamela-vectors` Parquet partitions to populate the 768-dimensional `embedding` column without local GPU calculation.
* **Linguistic Tagging:** Generate composite `salient_roots_text` (normalized lemmas + trilateral roots) via PyArabic / fast stemmer, calculate 512-byte MinHash signatures via `datasketch`, and commit into `shamela_corpus.db` with SQLite FTS5 index enabled.

### Milestone 2: Hybrid Retrieval & Automated Evaluation Core

* **Server-Side Query Vectorizer:** Embed incoming search queries via `fastembed` (`intfloat/multilingual-e5-base` quantized ONNX) on FastAPI CPU ($< 6\text{ ms}$), enforcing the mandatory `"query: "` prefix.
* **Hybrid Scoring Engine:** Implement Reciprocal Rank Fusion (RRF) combining SQLite FTS5 BM25 (lemmas + roots) and vector cosine similarity.
* **Contiguous Sibling Merger:** Automatically merge adjacent pages from the same book and section before clustering.
* **Boundary-Aware Expansion:** Implement `/api/v1/chunks/{id}/surrounding` utilizing `active_section_id` to resolve Level-2 context ($N-1 \leftrightarrow N+1$) without spilling across unrelated chapters.
* **SIMD Clustering & Thematic Grouping:** Partition candidate results by hierarchical TOC sections and cosine similarity.
* **Automated Evaluation Harness:** Run `scripts/benchmark_retrieval.py` over 500 samples from `ohsn/shamela_Qgen_2000samples` to verify **Recall@5 $\ge 85\%$** and **MRR $\ge 0.70$**.

### Milestone 3: Grounded Synthesis & AI Agent Protocols

* **SSE Stream Router:** Build `GET /api/v1/synthesis/stream` emitting `meta`, `token`, and `citations` frames via LiteLLM / local model.
* **Strict Footnote Grounding:** Formulate the LLM prompt contract to enforce exact citation anchors (`[^ref1]`, `[^ref2]`) tied 1:1 to database `chunk_id` and volume/page coordinates.
* **Agent Protocol (MCP):** Build `POST /api/v1/agent/tools/search_corpus` conforming to Model Context Protocol (MCP) standards, returning structured text, bookend context, and canonical permalinks.

### Milestone 4: Astro SSR & Reactive Island Workspace

* **Crawlable Permalinks:** Build `src/pages/p/[id].astro` rendering clean semantic HTML and Schema.org `ScholarlyArticle` JSON-LD with 0 KB client JavaScript for instant bot indexing.
* **Workspace Islands:** Implement `<SearchBar client:load/>` and `<PassageCard/>` with 3-tier depth toggles:
  * *Level 1 (مقتطف):* Compact snippet.
  * *Level 2 (سياق):* Sibling page context with boundary highlights.
  * *Level 3 (مطالعة):* Opens `<CitationDrawer client:idle/>` for full chapter reading.
* **State Coordination:** Bind DaisyUI drawer toggles and footnote citations directly to Nanostores (`$isDrawerOpen`, `$activeCitation`).

### Milestone 5: Gateway Routing, Deployment & Audit

* **Reverse Proxy (Zoraxy):** Configure single-domain routing (`/` and `/search` to Astro port 4321; `/api/v1/*` to FastAPI port 8000).
* **Production Container Stack:** Assemble `compose.yml` with read-only NVMe volume mounts for `shamela_corpus.db`.
* **Crawl & Latency Audit:** Verify first-byte delivery for search crawlers (`GPTBot`, `ClaudeBot`) and confirm end-to-end search latency stays under $15\text{ ms}$.

---

## 🎯 Verification & Quality Gates

| Milestone | Gate Criteria | Target Metric |
| :--- | :--- | :--- |
| **M1 Gate** | 10k passages indexed with FTS5 + 768-dim vectors | Execution $< 60\text{s}$ |
| **M2 Gate** | Automated retrieval benchmark over 500 QGen samples | **Recall@5 $\ge 85\%$**, **MRR $\ge 0.70$**, Latency $< 15\text{ms}$ |
| **M3 Gate** | Synthesis stream emits 100% verifiable `[^refN]` anchors | 0 hallucinated citation tags |
| **M4 Gate** | Astro SSR reader `/p/:id` rendered with 0 CLS | Raw HTML $< 2\text{ KB}$, 0 client JS |
| **M5 Gate** | Production Docker stack with zero-CORS reverse proxy | All healthchecks pass |