https://huggingface.co/datasets/AuthenticIlm/Shamela4_Full_DB
https://huggingface.co/datasets/MoMonir/Shamela_Books_info
https://huggingface.co/datasets/MoMonir/shamela_books_text
https://huggingface.co/datasets/MoMonir/shamela_books_text_full
https://huggingface.co/datasets/ieasybooks-org/shamela-waqfeya-library
https://huggingface.co/datasets/ieasybooks-org/shamela-waqfeya-library-compressed
https://huggingface.co/datasets/Kandil7/shamela-database
https://huggingface.co/datasets/freococo/synth_shamela_ocr_arabic_books
https://huggingface.co/datasets/Maktabati/shamela-vectors
https://huggingface.co/datasets/Maktabati/openiti-vectors
https://huggingface.co/datasets/Maktabati/shamela-bm25
https://huggingface.co/datasets/Kandil7/Athar-Shamela4

https://huggingface.co/datasets/ReligiousLLMs/shamela_all_diacritized_fully
https://huggingface.co/datasets/portakalmaymunu/shamelaws
https://huggingface.co/datasets/mhaamh19/shamelaws
https://huggingface.co/datasets/MathematicianNLPer/shamela_subset_wahhabite
https://huggingface.co/datasets/MathematicianNLPer/shamela_subset_not_wahhabite
https://huggingface.co/datasets/ohsn/shamela_Qgen_2000samples
https://huggingface.co/datasets/ohsn/shamela_Qgen_5000samples
https://huggingface.co/datasets/ohsn/shamela_Qgen_2000samples2
https://huggingface.co/datasets/Saheerakp/golden-shamela


This collection of 12 Hugging Face datasets contains critical resources for our architecture. Several of these solve the most labor-intensive tasks in the pipeline: **pre-built hierarchical Table of Contents (TOC) trees, pre-computed dense vector embeddings, and cross-referenced Hadith Isnād/Narrator tables.**

The datasets group into **5 functional tiers**:

```
                              HUGGING FACE CLASSICAL ARABIC ASSETS
                                                │
    ┌───────────────────┬───────────────────────┼───────────────────────┬───────────────────┐
    ▼                   ▼                       ▼                       ▼                   ▼
[ TIER 1: GOLDEN    [ TIER 2: TABULAR       [ TIER 3: PRE-COMPUTED  [ TIER 4: RAW ARCHIVE [ TIER 5: OCR
  STRUCTURED DB ]     PAGE EXPORTS ]          SEARCH ARTIFACTS ]      & PDF ARCHIVES ]      TRAINING ]
• AuthenticIlm      • MoMonir/Books_info    • Maktabati/vectors     • ieasybooks/waqfeya  • freococo/ocr
• Kandil7/Athar     • MoMonir/text_full     • Maktabati/openiti     • Kandil7/shamela-db
                                            • Maktabati/bm25

```

---

## Tier 1: Gold-Standard Structured Databases (TOC + Pages + Cross-References)

These are the most valuable datasets for our pipeline because they preserve the internal hierarchy of the books.

### 1. `AuthenticIlm/Shamela4_Full_DB` & 2. `Kandil7/Athar-Shamela4`

* **What it is:** A complete, modern extraction of Maktaba Shamela 4 (10M–100M tokens) organized by category (`01__العقيدة`, `07__شروح-الحديث`, etc.) and broken into clean per-book folders. `Kandil7/Athar-Shamela4` is an enhanced duplicate containing unified master catalogs and cross-reference Parquet tables.
* **Internal Anatomy per Book:**
* `pages.jsonl`: Sequential page records containing `page_num`, `part` (volume), `body` (clean text with minimal HTML tags), and separated `footnotes`.
* `toc.jsonl`: **Explicit Table of Contents tree** with `title_text`, `page_id`, and `parent_id` hierarchy.
* `book_metadata.json`: Author name, death year (*Hijri*), book classification, and publication data.
* `_meta/`: Cross-reference tables including `root_dictionary.parquet`, `narrators.parquet`, `hadith_xrefs.parquet`, `tafsir_xrefs.parquet`, and `page_isnads.parquet`.


* **Why this is essential:**
* **Eliminates Heading Regex Guesswork:** The `toc.jsonl` file provides the exact parent-child *Kitāb $\to$ Bāb $\to$ Faṣl* tree, removing the need to parse raw strings with `HeadingStackTracker`.
* **Accelerates Phase 3 Graph Construction:** The pre-extracted `narrators.parquet` and `page_isnads.parquet` give us a structured basis for our Hadith graph without running expensive LLM NER.


* **Verdict:** **Our primary dataset for corpus ingestion.**

---

## Tier 2: Clean Tabular Page-Level Corpora

### 3. `MoMonir/Shamela_Books_info`

### 4. `MoMonir/shamela_books_text` & 5. `MoMonir/shamela_books_text_full`

* **What it is:** A relational database export of Shamela (synced June 2025) comprising **8,538 books and 7,552,019 page rows** (~15.8 GB compressed CSV/Parquet).
* **Internal Anatomy:**
* `Shamela_Books_info`: Master bibliographic table (`book_id`, `book_name`, `author_id`, `author_death_hijri`, `category_id`, `publisher`, `editor`).
* `shamela_books_text_full`: `book_id`, `page_id`, `page_number`, `volume`, `body_text`, and a dedicated `footnotes` column.


* **Pros:**
* **Footnote Separation:** Footnotes (`¬١`, `¬٢`) are stored in a separate column, preventing commentary citations from polluting text bodies and degrading BM25 scores.
* **DuckDB Ingestion Speed:** Because it is distributed as standard Parquet/CSV, DuckDB can join `info` with `text_full` and populate a local database in under 60 seconds.


* **Cons:** Lacks the explicit `parent_id` hierarchical TOC links provided by `AuthenticIlm`.
* **Verdict:** The best single-file tabular fallback for bulk relational ingestion.

---

## Tier 3: Pre-Indexed Search Artifacts (Embeddings & FTS)

These artifacts eliminate hundreds of GPU hours by providing pre-calculated dense embeddings and search posting lists.

### 6. `Maktabati/shamela-vectors` & 7. `Maktabati/openiti-vectors`

* **What it is:** Pre-computed dense vector embeddings for the Shamela library (11.5M passages) and the OpenITI historical corpus (4.7M passages), updated mid-2026.
* **Internal Anatomy:** Parquet tables with passage identifiers mapped to normalized float arrays generated from multilingual Arabic retrieval models.
* **Why this is useful:**
* **Zero Ingestion Embedding Overhead:** Generating 384/768-dimensional embeddings for millions of passages on a single server GPU takes days. This dataset lets us load pre-computed vector tables directly into Turso/libSQL.
* **Cross-Corpus Compatibility:** Standardized schemas allow searching Shamela alongside OpenITI historical texts (chronicles, poetry, geographical dictionaries).


* **Verdict:** **Must-use for Dense Hybrid Search.** Download and load these vectors directly into libSQL vector tables.

### 8. `Maktabati/shamela-bm25`

* **What it is:** Pre-indexed SQLite databases (`bm25_shamela.db.zst`) with pre-built FTS5 / BM25 search indices.
* **Pros:** Allows instant lexical prototyping without running an ingestion pipeline.
* **Cons:** Built with standard SQLite FTS5 rather than Tantivy BM25 on Farasa-extracted roots.
* **Verdict:** Useful for quick sanity checks, but our custom Tantivy + Farasa index provides higher legal precision.

---

## Tier 4: Raw Document Archives & Raw Databases

### 9. `ieasybooks-org/shamela-waqfeya-library` & 10. `...-compressed`

* **What it is:** A massive archive (over 105 GB) combining Maktaba Shamela texts with **Al-Waqfeya printed PDF scans** (over 4,500 volumes across 40 categories).
* **Internal Anatomy:** Multi-part split ZIP archives (`pdf.z01` to `pdf.z08`, `txt.zip`, `docx.zip`, and `index.tsv`).
* **Why this is useful:**
* Provides the actual scanned PDF source pages corresponding to Shamela volume and page numbers.


* **Operational Role:** Not suitable for backend search indexing, but ideal for a secondary **"View Original Printed Page"** PDF viewer feature in the frontend.

### 11. `Kandil7/shamela-database`

* **What it is:** A 12 GB compressed archive (`database.rar`) containing raw binary `.mdb` (Microsoft Access) and `.sqlite` files extracted from the legacy desktop version of Maktaba Shamela.
* **Verdict:** Deprecated. Superseded by `AuthenticIlm/Shamela4_Full_DB` and `Kandil7/Athar-Shamela4`, which provide the same underlying data in modern Parquet and JSONL formats.

---

## Tier 5: Specialized OCR Model Training

### 12. `freococo/synth_shamela_ocr_arabic_books`

* **What it is:** Synthetic image-to-text paired data designed to train Optical Character Recognition (OCR) models (e.g., PaddleOCR, TrOCR) on classical Arabic fonts and typesetting layouts.
* **Verdict:** **Irrelevant for the Search Engine.** This dataset is meant for training vision models to digitize physical books, not for text retrieval or semantic clustering.

---

## Strategic Ingestion Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDED DATA INGESTION RECIPE                                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Metadata & Text Hierarchy:                                                          │
│    Use `AuthenticIlm/Shamela4_Full_DB` (or `Kandil7/Athar-Shamela4`)                   │
│    -> Gives clean text + exact `toc.jsonl` (Kitab/Bab/Fasl) + isolated footnotes.      │
│                                                                                        │
│ 2. Dense Vector Embeddings:                                                            │
│    Use `Maktabati/shamela-vectors`                                                     │
│    -> Ingest pre-calculated vectors into Turso without burning local GPU compute.      │
│                                                                                        │
│ 3. Phase 3 Hadith / Isnad Graph Data:                                                  │
│    Use `Kandil7/Athar-Shamela4/_meta/`                                                 │
│    -> Ingest `narrators.parquet` & `page_isnads.parquet` into Kùzu / relational tables.│
└────────────────────────────────────────────────────────────────────────────────────────┘

```


An analysis of the 9 Hugging Face datasets reveals that they group into **three distinct functional categories**:

1. **Full / Core Base Corpora** (Raw text, diacritized text, curated golden collections)
2. **Thematic / Ideological Subsets** (Madhhab / theological partitioning)
3. **Synthetic Question-Answering Evaluation Sets** (RAG benchmarking & SFT data)

---

### Global Taxonomy & Strategic Fit

```
                                 HUGGING FACE SHAMELA ECOSYSTEM
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
[ CORE BASE CORPORA ]               [ THEMATIC SUBSETS ]                    [ QA / RAG EVALUATION ]
• portakalmaymunu/shamelaws         • MathematicianNLPer/wahhabite          • ohsn/shamela_Qgen_2000samples
• mhaamh19/shamelaws                • MathematicianNLPer/not_wahhabite      • ohsn/shamela_Qgen_5000samples
• ReligiousLLMs/diacritized_fully                                           • ohsn/shamela_Qgen_2000samples2
• Saheerakp/golden-shamela
         │                                      │                                      │
         ▼                                      ▼                                      ▼
  Database Ingestion &                Bias / Perspective Testing             RAG Accuracy & Synthesis
  Tantivy BM25 Posting Lists          & Filtering Subsets                    Benchmarking Test Suite

```

---

## Group 1: Core Base Corpora & Raw Text

### 1. `ReligiousLLMs/shamela_all_diacritized_fully`

* **Provenance & Scope:** Curated by Abderrahman Skiredj / ReligiousLLMs (developers specializing in classical Arabic diacritization and *Tashkeel* neural models like *Ad-Dabit* and *Abbad*). This is a massive Parquet dataset (1M–10M rows) of Shamela texts with fully restored short vowels and diacritics.
* **Structural Anatomy:** Contains book metadata, raw text, and full vowel diacritics (*Fatḥah, Ḍammah, Kasrah, Sukūn, Shaddah, Tanwīn*).
* **Pros:**
* **Frontend Visual Fidelity:** Perfect for the Astro SSR reader view (`/p/:id`). Classical Arabic prose rendered with full vocalization improves readability for non-native Arabic scholars.
* **TTS & Phonetic Search:** Enables downstream Text-to-Speech and exact morphological disambiguation.


* **Bottlenecks for our Stack:**
* Diacritics break standard whitespace and BM25 tokenizers. If indexed directly into Tantivy, `"قَلْبُ"` and `"قَلْبَ"` would be treated as distinct terms.
* **Action Required:** You must run `pyarabic.araby.strip_tashkeel()` during ingestion to create the normalized `salient_roots_text` column while keeping this diacritized string in `raw_text` for visual display.



---

### 2. `portakalmaymunu/shamelaws` & 3. `mhaamh19/shamelaws`

* **Provenance & Scope:** Raw tabular/CSV/Parquet scrapes extracted directly from `shamela.ws` (the official modern online web archive of Maktaba Shamela).
* **Structural Anatomy:** Typically structured with: `book_id`, `page_id`/`page_num`, `part`/`vol`, and `text` (body paragraph content).
* **Pros:**
* **Clean Web-Aligned Indexing:** Direct 1:1 parity with official `shamela.ws` volume and page references (*Juz'* and *Safḥah*), making legal citations verifiable in print editions.
* **High Throughput Ingestion:** Pre-formatted in CSV/Parquet, allowing DuckDB to ingest millions of rows into Turso in seconds.


* **Bottlenecks for our Stack:**
* **No Native Hierarchy Markers:** These raw scrapes often concatenate *Bab* and *Fasl* headings directly into the text body without explicit metadata tags (`section_level`, `section_title`).
* **Action Required:** You must run our regex-based `HeadingStackTracker` during the Prefect flow to rebuild the hierarchical breadcrumb tree before inserting records into libSQL.



---

### 4. `Saheerakp/golden-shamela`

* **Provenance & Scope:** A curated "Golden" subset filtering the bloated 7,000+ book Shamela catalog down to the canonical reference works (*Ummāt al-Kutub*)—the 4 Sunni Fiqh schools, the 6 canonical Hadith books (*Kutub al-Sittah*), foundational Tafsirs (Tabari, Qurtubi, Ibn Kathir), and major dictionaries (*Lisan al-Arab*).
* **Structural Anatomy:** Cleaned, deduplicated book records focused on high-authority classical authors (1st–8th century AH).
* **Pros:**
* **Ideal for MVP Phase 1:** Eliminates modern low-quality tracts, OCR scan errors, and redundant duplicate editions that pollute the full 5.91M dataset.
* **High Signal-to-Noise Ratio:** Bitset Jaccard clusters will be tighter and more coherent because terminology is strictly classical.


* **Strategic Role:** **Use this as your primary dataset for your 10k–50k passage local benchmark test.**

---

## Group 2: Thematic & Ideological Subsets

### 5. `MathematicianNLPer/shamela_subset_wahhabite`

* **Provenance & Scope:** A targeted ideological partition containing works by Najdi Hanbali/Salafi scholars (e.g., Ibn Taymiyyah, Ibn al-Qayyim, Muhammad b. Abd al-Wahhab, and later Najdi jurists like *Al-Durar al-Saniyyah*).
* **Structural Anatomy:** Filtered passage records mapped to specific author metadata and theological treatises.
* **Pros & Use Case:** Useful for testing school-specific RAG queries (e.g., verifying Athari/Salafi legal preferences on *Asma wa Sifat* or commercial transactions).
* **Cons:** Heavily skewed toward late-medieval and modern Hanbali/Najdi discourse; cannot serve as a comprehensive cross-madhhab corpus.

---

### 6. `MathematicianNLPer/shamela_subset_not_wahhabite`

* **Provenance & Scope:** The complementary counter-subset: Ash'ari, Maturidi, early classical multi-madhhab jurists (Hanafi, Maliki, Shafi'i, early Hanbali), Sufi manuals (*Ihya Ulum al-Din*, *Risalah al-Qushayriyyah*), and non-Najdi texts.
* **Structural Anatomy:** Parquet-converted dataset containing classical scholastic works across theology, jurisprudence, and spiritual discourse.
* **Strategic Role for our Stack:**
* Pairing `#5` and `#6` provides a **Dialectical Evaluation Benchmark**. You can test whether your Tantivy BM25 + Bitset Jaccard engine can accurately partition cross-school debates (e.g., how Ghazali vs. Ibn Taymiyyah define *Ta'weel* or *Al-Aql*) into distinct, unmixed thematic clusters.



---

## Group 3: Synthetic QA & RAG Evaluation Datasets

### 7. `ohsn/shamela_Qgen_2000samples`

### 8. `ohsn/shamela_Qgen_5000samples`

### 9. `ohsn/shamela_Qgen_2000samples2`

* **Provenance & Scope:** Synthetic Question-Generation (QGen) datasets created using frontier LLMs over Shamela passage chunks.
* **Structural Anatomy:** Contains triples:

$$\{\text{`question` (Natural Arabic/English), } \text{`context` (Classical passage), } \text{`ground_truth_answer` (Synthesized text)}\}$$


* **Pros:**
* **Ready-Made RAG Benchmark:** Gives you 9,000 ready-to-evaluate query test cases to measure your search engine's **Recall@K**, **MRR (Mean Reciprocal Rank)**, and citation accuracy.
* **Multilingual Fine-Tuning:** Excellent for validating whether client-side dense vectors (Transformers.js) accurately bridge natural language user queries to classical Arabic text chunks.


* **Cons:**
* Because these are synthetic triples, questions may occasionally use modern phrasing or misinterpret rare classical juristic idioms (*Gharīb al-Fiqh*).
* Not an ingestion corpus—strictly an **evaluation and test suite**.



---

## Strategic Dataset Utilization Matrix

| Dataset | Dataset Role | Target Pipeline Component | Actionable Implementation |
| --- | --- | --- | --- |
| **`Saheerakp/golden-shamela`** | **Primary MVP Data** | Ingestion & Storage | **Ingest this first** to validate Tantivy BM25, libSQL indexing, and Astro UI. |
| **`ReligiousLLMs/diacritized`** | **Display Layer** | Database `raw_text` | Store as display text; strip diacritics for `salient_roots_text`. |
| **`portakalmaymunu/shamelaws`** | **Full Scale Production** | Complete 5.91M Ingest | Use for full corpus build via DuckDB $\to$ Turso. |
| **`ohsn/shamela_Qgen_*`** | **Automated Benchmark** | Evaluation Harness | Use as test queries to measure Search Latency and Retrieval Precision. |
| **`MathematicianNLPer/*`** | **Dialectical Testing** | Bitset Jaccard Partitioner | Validate multi-perspective clustering on theology & Fiqh debates. |