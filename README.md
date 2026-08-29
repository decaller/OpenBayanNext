# OpenBayan (بيان) — Classical Arabic Semantic Search & Scholarly Corpus Engine

<p align="center">
  <img src="apps/web/public/favicon.svg" alt="OpenBayan Logo" width="80" height="80" />
</p>

<p align="center">
  <strong>A high-throughput, low-latency Information Retrieval (IR) and thematic synthesis platform engineered specifically for classical Islamic scholarly corpora.</strong>
</p>

<p align="center">
  <a href="#-project-vision--philosophy">Vision</a> •
  <a href="#-corpus-sources--heritage">Corpus Sources</a> •
  <a href="#-data-processing--indexing-pipeline">Data Pipeline</a> •
  <a href="#-hybrid-retrieval--search-engine">Search Engine</a> •
  <a href="#-backend-api-specification">Backend API</a> •
  <a href="#-frontend-architecture--features">Frontend & UI</a> •
  <a href="#-monorepo-structure">Repository Layout</a> •
  <a href="#-quickstart--deployment">Deployment</a>
</p>

---

## 🌟 Project Vision & Philosophy

Classical Arabic scholarship is characterized by rich morphological structures, complex intertextuality, multi-century commentary traditions (*Shurūḥ*), and strict hierarchical structures (*Kitāb $\to$ Bāb $\to$ Faṣl*). Traditional search tools in this domain either rely on rudimentary substring matching (failing across grammatical derivations and orthographic variations) or heavy, opaque LLM wrappers that hallucinate citations.

**OpenBayan (بيان)** solves this through an embedded, zero-network-overhead architecture built on four core principles:

1. **Embedded / In-Process Read Path**: The entire relational metadata, Table of Contents tree, SQLite FTS5 BM25 index, and 768-dimensional dense vector embeddings are consolidated into a single self-contained database (`data/shamela_corpus.db`) mounted directly on local NVMe storage, achieving sub-10ms search query latencies without external vector database dependencies.
2. **Morphological Root & Lemma Indexing**: Pure Python morphological tokenization normalizes Arabic orthography, strips diacritics (*Tashkīl*) and justification markers (*Kashīdah*), and constructs space-delimited composite tokens combining surface forms, lemmas, and trilateral roots.
3. **Multi-Tier Context Resolution**: Search hits are not isolated snippets; the engine provides 3-tier elastic context:
   - **Level 1 (Atomic Passage)**: The specific matching page/chunk.
   - **Level 2 (Discourse Triad $N \pm 1$)**: Surrounding context respecting chapter and book boundaries.
   - **Level 3 (Continuous Chapter Stream)**: Full section reading via bidirectional slide-out drawer streaming.
4. **Verifiable Scholarly Attribution**: Every passage preserves authentic volume and page numbers from historical print editions and provides direct deep links to primary digital libraries (**Turath.io** and **Al-Maktaba Al-Shamela**), as well as 1-click structured prompt formatting for AI/LLM grounding.

---

## 📚 Corpus Sources & Heritage

The initial corpus index comprises **60 canonical masterworks** representing the core disciplines of classical Islamic sciences:

```
                               CANONICAL CORPUS (60 Masterworks)
                                              │
    ┌──────────────────┬──────────────────────┼──────────────────────┬──────────────────┐
    ▼                  ▼                      ▼                      ▼                  ▼
[ Hadith & Sunnah ]  [ Hadith Commentary ]  [ Jurisprudence (Fiqh) ] [ Quranic Tafsir ] [ Creed (Aqeedah) ]
• Sahih al-Bukhari   • Fath al-Bari (Ibn Hajar) • Al-Majmu' (Nawawi/Subki)• Tafsir al-Tabari • Sharh al-Tahawiyyah
• Sahih Muslim       • Umdat al-Qari (Ayni) • Al-Mughni (Ibn Qudamah)  • Tafsir Ibn Kathir • Kitab al-Tawhid
• Sunan Abi Dawud    • Sharh Sahih Muslim   • Bidayat al-Mujtahid      • Tafsir al-Qurtubi • Al-Aqidah al-Wasitiyyah
• Jami' al-Tirmidhi  • Irshad al-Sari       • Al-Mudawwanah            • Tafsir al-Baghawi • Al-Ibana (Ash'ari)
```

### Dataset Provenance & Ingestion Assets
- **`AuthenticIlm/Shamela4_Full_DB`**: Primary extraction of Shamela 4, providing explicit `toc.jsonl` tree hierarchies and clean text/footnote separation.
- **`Kandil7/Athar-Shamela4`**: Enhanced cross-reference metadata tables and narrator identity maps.
- **`Maktabati/shamela-vectors`**: Pre-computed 768-dimensional embeddings generated with multilingual E5 models (`Xenova/multilingual-e5-base`).

### Storage & Ingestion Footprint

| Metric | Measured Value | Description |
|---|---|---|
| **Total Canonical Books** | `60` | Full master bibliographic entries with author death years (A.H.) |
| **Hierarchical Section Nodes** | `97,533` | Pre-calculated parent-child Table of Contents tree nodes |
| **Total Content Passages** | `76,274` | Content pages with pre-separated body text and footnotes |
| **Dense Vector Embeddings** | `234.3 MB` | 768-dimensional float32 IEEE 754 vectors stored as binary BLOBs |
| **Text, TOC & FTS5 Index** | `252.7 MB` | Full raw text, B-tree indexes, and FTS5 inverted posting lists |
| **Total Database File Size** | **`487.0 MB`** | Single self-contained SQLite/libSQL database file |

---

## ⚙️ Data Processing & Indexing Pipeline

The offline pipeline (`apps/api/pipeline/`) ingests raw dataset exports into the optimized single-file database:

```
┌─────────────────────────────────────────────────────────────┐
│ DATA SOURCES (`data/samples/`)                              │
│ • `metadata.json` • `toc.jsonl` • `pages.jsonl` • Vector BLOBs │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ INGESTION WORKER (`apps/api/pipeline/`)                     │
│                                                             │
│ 1. `stemmer.py` (Zero-JVM Morphological Normalizer)         │
│    • Unifies Alef variants (أ/إ/آ/ٱ -> ا), Taa Marbutah (ة)  │
│    • Strips Tashkeel diacritics and Kashida tatweel         │
│    • Filters classical particle stopwords                   │
│    • Extracts space-delimited composite roots & lemmas      │
│                                                             │
│ 2. `toc_resolver.py` (Hierarchical Interval Tree Mapper)    │
│    • Maps Kitāb -> Bāb -> Faṣl headings to physical pages   │
│    • Pre-calculates complete structural breadcrumb paths    │
│                                                             │
│ 3. `ingest.py` (High-Throughput SQLite Bulk Loader)         │
│    • 64 KB page size, synchronous NORMAL batching           │
│    • Native FTS5 rebuild (unicode61 tokenizer)              │
│    • Post-ingestion WAL checkpoint truncation               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: `data/shamela_corpus.db` (487 MB)                   │
│ • `books` • `sections` • `prepared_chunks` • `prepared_chunks_fts` │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Hybrid Retrieval & Search Engine

OpenBayan employs a dual-path hybrid ranking pipeline that fuses lexical precision with dense semantic understanding:

```
                            DUAL-PATH HYBRID RETRIEVAL PIPELINE
                            
      User Query: "شروط بيع السلم" / "إنما الأعمال بالنيات" / "البخاري 1"
                                     │
      ┌──────────────────────────────┴──────────────────────────────┐
      ▼                                                             ▼
[ Scripture Citation Interceptor ]                           [ Query Expander ]
  • Regex parser detects direct citations                      • Disjunctive lemma expansion:
    (e.g., "البخاري 1" / "البقرة 255")                           (الاعمال OR اعمال OR عمل) AND (بالنيات OR نيات)
  • Injects Pinned Scripture Card                              • 3-letter root over-stripping protection
      │                                                             │
      │                                    ┌────────────────────────┴────────────────────────┐
      │                                    ▼                                                 ▼
      │                          [ SQLite FTS5 BM25 ]                             [ CPU ONNX Vectorizer ]
      │                            • `salient_roots_text` search                    • `multilingual-e5-base`
      │                            • BM25 rank score calculation                    • Asymmetric prefix: `query: <text>`
      │                            • Candidate Top 50 hits                          • RAM Vector Matrix cosine dot-product
      │                                    │                                                 │
      │                                    └────────────────────────┬────────────────────────┘
      │                                                             │
      │                                                             ▼
      │                                             [ Reciprocal Rank Fusion (RRF) ]
      │                                               • $RRF(d) = \frac{0.5}{60 + r_{bm25}} + \frac{0.5}{60 + r_{vec}}$
      │                                                             │
      │                                                             ▼
      │                                             [ Contiguous Sibling Merger ]
      │                                               • Fuses adjacent pages ($N, N+1$) from same section
      │                                               • Joins volume/pages: "ج 1 ص 526 - ج 1 ص 527"
      │                                               • Fused relevance score: $\max(Score_A, Score_B) \times 1.05$
      │                                                             │
      │                                                             ▼
      └────────────────────────────────────────────────────────► [ SearchResponse JSON ]
                                                                    │
                                                                    ▼
                                                    [ Frontend Thematic Clustering ]
                                                      • SIMD Jaccard + Vector theme grouping
                                                      • Accuracy-ranked descending ($96\% \to 91\% \to 78\%$)
```

### Key Retrieval Subsystems
- **Reciprocal Rank Fusion (RRF)**: Balances exact terminology matches (essential for specific Fiqh terms like *ʿArāyā* or *Mukhābarah*) with semantic intent.
- **In-Memory RAM Vector Matrix**: Caches normalized 768-dim embeddings in backend memory, executing cosine similarity dot products in under $4\text{ ms}$.
- **Contiguous Sibling Merger**: Solves the "split-page dilemma" where a continuous scholarly argument spans across page boundaries by dynamically fusing consecutive page chunks into unified reading cards.
- **Thematic Clusterer**: Partitions search results into coherent topic clusters dynamically sorted by whole-sentence query accuracy descending.

---

## 🌐 Backend API Specification

The backend is built with **FastAPI** and utilizes asynchronous `libsql_client` for zero-overhead local database communication.

### Core Endpoints

| Method | Endpoint | Description | Key Parameters |
|---|---|---|---|
| `GET` | `/api/v1/search` | Paginated hybrid search | `q`, `mode` (`hybrid`\|`fts`\|`vector`), `category`, `era`, `tradition`, `limit` |
| `GET` | `/api/v1/chunks/{id}` | Level 1: Passage detail & metadata | `id` (Chunk integer ID) |
| `GET` | `/api/v1/chunks/{id}/surrounding` | Level 2: Surrounding context ($N \pm 1$) | `id`, boundary invariants (`is_same_section`) |
| `GET` | `/api/v1/books` | Catalog of all canonical books | `category`, `era` filters |
| `GET` | `/api/v1/books/{id}/toc` | Hierarchical Table of Contents tree | `id` (Book ID) |
| `GET` | `/api/v1/books/{id}/sections/{sec_id}/chunks` | Level 3: Continuous chapter stream | `id`, `sec_id`, `cursor`, `direction` |
| `GET` | `/health` | Diagnostic & vector cache healthcheck | — |

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

## 🎨 Frontend Architecture & UI Features

The web frontend (`apps/web/`) is built with **Astro 5** (SSR Mode via `@astrojs/node`), **Tailwind CSS v4**, **daisyUI 5**, and **React 19** client islands.

```
apps/web/src/
├── assets/
│   └── app.css                   # Tailwind v4, daisyUI 5, font imports & custom utilities
├── components/
│   ├── astro/                    # Zero-JS Static Server Components
│   │   ├── Header.astro          # Sticky navbar with dynamic scroll logo & theme switcher
│   │   ├── Footer.astro          # Mission, library links, API telemetry & live sync badge
│   │   ├── PassageCard.astro     # Core scholarly passage card with context blocks & copy tools
│   │   └── ThemeSwitcher.astro   # Multi-theme selector dropdown
│   └── islands/                  # React 19 Interactive Client Islands
│       ├── SearchBar.tsx         # Search input with '/' hotkey & retrieval mode toggles
│       ├── CitationDrawer.tsx    # Slide-out continuous reading drawer with bidirectional loading
│       ├── SearchControls.tsx    # Reading settings (Font size, Context depth, Highlights)
│       └── LanguageSwitcher.tsx  # Trilingual switcher (Arabic, English, Indonesian)
├── layouts/
│   └── BaseLayout.astro          # HTML shell, SEO OpenGraph, JSON-LD, and theme script
├── lib/
│   ├── api.ts                    # Backend API client & TypeScript response schemas
│   ├── i18n.ts                   # Trilingual translations & AI citation prompt formatters
│   ├── thematic_clusterer.ts     # SIMD Jaccard & accuracy-ranked thematic partitioning
│   └── highlighter.ts            # Arabic query term highlighter
├── pages/
│   ├── index.astro               # Homepage with hero emblem, quick prompts & features
│   ├── search.astro              # Unified zero-pagination thematic search workspace
│   └── p/
│       └── [id].astro            # 0-JS SSR canonical permalink page (Schema.org JSON-LD)
└── stores/
    └── workspace.ts              # Nanostores reactive state bridge (Drawer, Fonts, Themes)
```

### High-Value Scholarly Features
1. **0-JS SSR Canonical Permalinks (`/p/:id`)**: Ultra-fast, SEO-optimized static HTML permalinks for individual passages with zero client JavaScript bundle, embedded Schema.org `ScholarlyArticle` structured data, and pre-rendered Level 2 context.
2. **Slide-Out Continuous Reader (`CitationDrawer`)**: Slide-out drawer allowing researchers to read full chapters continuously with bidirectional chunk expansion (*Load Earlier Passages* / *Load Subsequent Passages*).
3. **2-Level Context Depth Switcher**:
   - **Level 1 (Atomic)**: Clean focused snippet.
   - **Level 2 (Discourse Triad)**: Displays preceding ($N-1$) and succeeding ($N+1$) discourse blocks directly inside the search stream.
4. **Trilingual Localization (i18n)**: Native UI translation support across **Arabic (`ar`)**, **English (`en`)**, and **Indonesian (`id`)**.
5. **AI Grounding & Citation Exporter**: 1-click generation of structured Markdown prompts containing volume, page, section breadcrumb, author death year, and full matn for direct input into LLMs.

---

## 🏗️ Monorepo Structure

The project is structured as a polyglot monorepo managed via **Turborepo** and **pnpm workspaces**:

```
OpenBayanNext/
├── apps/
│   ├── api/                      # FastAPI Backend & Search Engine
│   │   ├── app/                  # Application code (API, Core, Services, Schemas)
│   │   ├── pipeline/             # Data ingestion, stemmer, and TOC resolver scripts
│   │   ├── Dockerfile            # Python 3.12 production container
│   │   └── requirements.txt      # Backend Python dependencies
│   └── web/                      # Astro Web Frontend
│       ├── src/                  # Astro pages, layouts, and React islands
│       ├── astro.config.mjs      # Astro SSR configuration
│       ├── Dockerfile            # Multi-stage production container
│       └── package.json          # Frontend dependencies
├── audit/                        # Comprehensive UI/UX and design audit documentation
│   ├── DESIGN_AND_COLOR_AUDIT.md # Complete multi-theme audit report
│   └── README.md                 # Audit index
├── data/                         # Local database and sample corpus storage
│   └── shamela_corpus.db         # Self-contained SQLite/libSQL database (487 MB)
├── dev_notes/                    # Engineering milestone walkthroughs and benchmarks
│   ├── 01_milestone_1_ingestion_and_indexing_walkthrough.md
│   ├── 02_milestone_2_hybrid_retrieval_walkthrough.md
│   └── 03_milestone_3_astro_ssr_walkthrough.md
├── compose.yml                   # Docker Compose & Portainer Stack configuration
├── package.json                  # Workspace scripts
├── pnpm-workspace.yaml           # Monorepo package definitions
└── turbo.json                    # Turborepo task pipeline
```

---

## 🚀 Quickstart & Deployment

### Prerequisites
- **Node.js**: `>= 22.12.0`
- **pnpm**: `>= 10.0.0`
- **Python**: `>= 3.12`
- **Docker & Docker Compose** (optional for containerized deployment)

### 1. Local Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/OpenBayanNext.git
cd OpenBayanNext

# Install frontend and workspace dependencies
pnpm install

# Setup backend Python virtual environment
pnpm setup:api

# Start both Astro Frontend and FastAPI Backend in parallel
pnpm dev
```

- **Frontend Web UI**: [http://localhost:4321](http://localhost:4321)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Verification & Benchmark Test Suites

You can run the end-to-end verification suites across all three engineering milestones:

```bash
# Milestone 1: Ingestion, schema, and FTS5 verification
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/verify_milestone1.py

# Milestone 2: Vectorizer warmup, hybrid RRF search, and context engine
apps/api/.venv/bin/python dev_notes/02_milestone_2_hybrid_retrieval/verify_milestone2.py

# Milestone 3: Full-stack Astro SSR, 0-JS permalinks, and UI endpoints
apps/api/.venv/bin/python dev_notes/03_milestone_3_astro_ssr/verify_milestone3.py
```

### 3. Production Build & Docker Deployment

```bash
# Build production bundles
pnpm build

# Run via Docker Compose
docker compose up --build
```

---

## 👥 Contact & Maintainer

- **Maintainer**: **Harridi Ilman Tovid**
- **WhatsApp**: [+62 811-1729-896](https://wa.me/628111729896)
- **GitHub Repository**: [https://github.com/decaller/OpenBayanNext](https://github.com/decaller/OpenBayanNext)

---

## 📜 License & Scholarly Openness

OpenBayan is developed as an open-source scholarly research platform. Classical corpus texts and datasets originate from public domain Islamic heritage archives (Maktaba Shamela, Turath.io, and Al-Waqfeya).
