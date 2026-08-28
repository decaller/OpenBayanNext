# OpenBayan Classical Arabic Search & Reading Engine: Minimalist MVP Milestones

A focused, high-performance content search and reading platform for classical Islamic texts. Built with zero GPU embedding overhead, zero Java/JVM bloat, zero complex graph databases, and zero LLM hallucination risk.

---

## 🧭 MVP Milestone Overview

| Milestone | Core Deliverable | Primary Tech & Data Assets | Validation Gate |
| :--- | :--- | :--- | :--- |
| **M1: Lean Ingestion & Indexing** | Ingest `pages.jsonl` + `toc.jsonl`, join pre-computed vectors, generate `Tashaphyne` stems, build single-file DB. | `AuthenticIlm`, `Maktabati/vectors`, `PyArabic`, `Tashaphyne`, SQLite/libSQL | 10k passages indexed with FTS5 BM25 + 768-dim Vectors in $< 90\text{s}$ (Zero JVM). |
| **M2: Hybrid Retrieval & Context Engine** | Hybrid search (FTS5 BM25 + Vector Cosine), contiguous sibling merger, 3-tier context resolution. | FastAPI, `fastembed` (CPU E5), SQLite FTS5 | Combined hybrid search + sibling merge latency $< 8\text{ ms}$. |
| **M3: Astro SSR & DaisyUI Reader Islands** | 0-JS permalinks (`/p/:id`), responsive search workspace, slide-out full chapter reading drawer. | Astro SSR, React, DaisyUI, Nanostores, Tailwind CSS | 0 KB client JS on `/p/:id`, smooth 60 FPS drawer opening. |
| **M4: Container Gateway & Crawler Verification** | Single-domain Docker Compose stack behind Zoraxy with read-only NVMe mounts. | Zoraxy, Docker Compose, Linux NVMe | 100% first-byte text delivery for crawlers; single-domain zero-CORS. |

---

## 🏗️ Architecture Flow

```
                      LEAN CONTENT SEARCH ARCHITECTURE
                      
      User Search Query: "شروط بيع السلم في المذهب الشافعي"
                    │
                    ▼
    ┌──────────────────────────────────────────────┐
    │ FASTAPI QUERY HANDLER                        │
    │ • Normalize text (PyArabic)                  │
    │ • Generate search stems (Tashaphyne)         │
    │ • Encode vector query (fastembed on CPU)     │
    └──────────────────────┬───────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────┐
    │ SQLite / libSQL EMBEDDED DATABASE            │
    │ • FTS5 BM25 on text stems (`unicode61`)      │
    │ • Vector Cosine distance (768-dim E5)        │
    │ • Join contiguous sibling pages (N-1, N, N+1)│
    └──────────────────────┬───────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────┐
    │ ASTRO SSR FRONTEND                           │
    │ • Render instant HTML search result cards    │
    │ • Slide open chapter reading drawer          │
    │ • 0-JS static permalinks (/p/:id)            │
    └──────────────────────────────────────────────┘
```

---

## 📋 Milestone Breakdown

### Milestone 1: Lean Ingestion & Indexing Pipeline

* **Source Extraction:** Stream canonical books from `AuthenticIlm/Shamela4_Full_DB` in `data/samples/` (`pages.jsonl` and `toc.jsonl`).
* **Hierarchy Forward-Fill:** Map parent-child headings from `toc.jsonl` directly to each page's `page_id` to establish `section_title`, `section_level` (*Kitāb $\to$ Bāb $\to$ Faṣl*), and breadcrumbs.
* **Footnote Isolation:** Store body text in `raw_text` and route editorial commentary to a separated `footnotes` column to prevent BM25 score corruption.
* **Vector Alignment:** Join `(book_id, page_id)` directly against `Maktabati/shamela-vectors` Parquet files to populate the 768-dim `embedding` column without local GPU compute.
* **Java-Free Stemming:** Use `PyArabic` and `Tashaphyne` to generate normalized composite stems (`salient_roots_text`) for SQLite FTS5 indexing.
* **Database Target:** Write records into a local single-file `shamela_corpus.db` with SQLite FTS5 full-text search and vector BLOB storage enabled.

### Milestone 2: FastAPI Hybrid Retrieval & Context Resolution

* **CPU Query Vectorizer:** Embed runtime queries via `fastembed` (`intfloat/multilingual-e5-base`) in $< 5\text{ ms}$ on CPU with the mandatory `"query: "` prefix.
* **Hybrid Scoring Router:** Implement `/api/v1/search` combining FTS5 BM25 stem scores and vector cosine similarities using Reciprocal Rank Fusion (RRF).
* **Contiguous Sibling Merger:** Detect when search results return adjacent pages from the same book ($N, N+1$) and merge them into unified, readable passage blocks.
* **3-Tier Context Resolvers:**
  * *Level 1 (Atomic):* Single-page hit snippet.
  * *Level 2 (Discourse):* Surrounding sibling context ($N-1 \leftrightarrow N+1$) respecting section boundaries via `/api/v1/chunks/{id}/surrounding`.
  * *Level 3 (Chapter):* Stream consecutive chunks for full-chapter reading via `/api/v1/books/{id}/sections/{section_id}/chunks`.

### Milestone 3: Astro SSR Frontend & DaisyUI Reader Islands

* **0-JS SEO Permalinks:** Build `src/pages/p/[id].astro` delivering instant, pre-rendered semantic HTML with Schema.org `ScholarlyArticle` metadata and zero client JavaScript overhead.
* **Search Workspace Island:** Create `src/pages/search.astro` featuring `<SearchBar client:load/>` and `<PassageCard/>` with an inline 3-tier depth switcher:
  * `مقتطف` (Snippet view)
  * `سياق` (Expanded adjacent context)
  * `مطالعة ↗` (Full-chapter view)
* **Slide-Out Reading Drawer:** Implement `<CitationDrawer client:idle/>` using controlled DaisyUI classes bound to Nanostores (`$isDrawerOpen`, `$activeCitation`) for reading entire chapters without page reloads.
* **Typography & RTL:** Configure Tailwind with classical Arabic font stacks (`Amiri`, `Traditional Arabic`) and high-contrast paper tones.

### Milestone 4: Production Containerization & Crawler Verification

* **Gateway Configuration:** Route both services behind Zoraxy (`/` and `/search` to Astro on port 4321; `/api/v1/*` to FastAPI on port 8000).
* **Production Containerization:** Assemble a lean `compose.yml` deploying Astro (Node SSR) and FastAPI with the database mounted as read-only (`:ro`).
* **Latency & SEO Audit:** Validate that search API response times remain under $10\text{ ms}$ and verify that bots (`GPTBot`, `ClaudeBot`, `curl`) extract complete passage text from first-byte HTML responses.

---

## 🎯 Verification Gates

| Milestone | Gate Criteria | Target Metric |
| :--- | :--- | :--- |
| **M1 Gate** | 10k passages indexed with FTS5 + 768-dim vectors | Execution $< 90\text{s}$, 0 Java dependencies |
| **M2 Gate** | Combined hybrid search + sibling merge | Latency $< 8\text{ ms}$ |
| **M3 Gate** | Astro SSR reader `/p/:id` rendered with 0 CLS | Raw HTML $< 2\text{ KB}$, 0 client JS |
| **M4 Gate** | Production Docker stack with Zoraxy single-domain | 100% bot first-byte crawl pass, $< 10\text{ms}$ API SLA |