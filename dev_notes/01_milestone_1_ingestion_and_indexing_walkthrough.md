# Milestone 1: Lean Ingestion & Indexing Pipeline — Complete Walkthrough

This document provides the complete architecture summary, schema specifications, benchmark metrics, storage breakdown, and hands-on testing instructions for **Milestone 1**.

---

## 🎯 Architectural Overview & What Was Built

```
                          INGESTION & INDEXING PIPELINE
                          
    ┌─────────────────────────────────────────────────────────────┐
    │ DATA SOURCES (`data/samples/`)                              │
    │ • AuthenticIlm: `pages.jsonl`, `toc.jsonl`, `metadata.json` │
    │ • Maktabati: Pre-computed 768-dim E5 Vector Embeddings      │
    └──────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
    ┌─────────────────────────────────────────────────────────────┐
    │ INGESTION WORKER (`apps/api/pipeline/`)                     │
    │ 1. `toc_resolver.py`: Pre-calculates Kitab/Bab/Fasl tree    │
    │ 2. `stemmer.py`: Pure Python PyArabic + Tashaphyne stems    │
    │ 3. `ingest.py`: High-throughput native SQLite3 bulk loader  │
    └──────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
    ┌─────────────────────────────────────────────────────────────┐
    │ OUTPUT: `data/shamela_corpus.db` (487 MB)                   │
    │ • `books`: 60 Master Bibliographic Records                  │
    │ • `sections`: 97,533 Hierarchical TOC Navigation Nodes      │
    │ • `prepared_chunks`: 76,274 Content Pages + 768-dim BLOBs   │
    │ • `prepared_chunks_fts`: SQLite FTS5 BM25 Virtual Table     │
    └─────────────────────────────────────────────────────────────┘
```

---

## 📁 Key Files & Core Components

1. **[`stemmer.py`](file:///home/abuhafi/Project/OpenBayanNext/apps/api/pipeline/stemmer.py)**:
   * **Zero JVM / Pure Python:** Powered by `PyArabic` and `Tashaphyne`.
   * **Deterministic Normalization:** Unifies Alef variants (`أ/إ/آ/ٱ` $\rightarrow$ `ا`), Taa Marbutah (`ة` $\rightarrow$ `ه`), and Alif Maqsura (`ى` $\rightarrow$ `ي`). Strips Tashkeel, Tatweel/Kashida, and classical stopword particles.
   * **Composite Tokens:** Generates space-delimited composite **Lemmas + Trilateral Roots** (`salient_roots_text`) for high-precision FTS5 scoring.

2. **[`toc_resolver.py`](file:///home/abuhafi/Project/OpenBayanNext/apps/api/pipeline/toc_resolver.py)**:
   * **Tree Interval Mapping:** Maps parent-child headings (*Kitāb $\to$ Bāb $\to$ Faṣl*) from `toc.jsonl` directly to physical pages.
   * **Pre-Computed Breadcrumbs:** Pre-calculates the complete hierarchical navigation path at tree construction time.
   * **Edge-Case Handling:** Handles pre-TOC front matter (*Muqaddimah*) and multi-heading collisions per page.

3. **[`schema.py`](file:///home/abuhafi/Project/OpenBayanNext/apps/api/pipeline/schema.py)**:
   * **`books`**: Master bibliographic metadata table.
   * **`sections`**: Hierarchical TOC section nodes table.
   * **`prepared_chunks`**: Passages content table with denormalized `book_name`, `salient_roots_text`, and 768-dim `embedding BLOB` column for vector cosine similarity.
   * **`prepared_chunks_fts`**: SQLite FTS5 virtual table with `unicode61 remove_diacritics 0` and unindexed metadata columns.

4. **[`ingest.py`](file:///home/abuhafi/Project/OpenBayanNext/apps/api/pipeline/ingest.py)**:
   * Native `sqlite3` batching with 64KB page size and transaction commits.
   * Single-pass FTS5 bulk index rebuild (`INSERT INTO prepared_chunks_fts(prepared_chunks_fts) VALUES('rebuild')`).
   * **Docker Hardening:** Post-ingestion WAL truncation (`PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode = DELETE;`) to ensure 100% lock-free read-only Docker mounting.

5. **[`database.py`](file:///home/abuhafi/Project/OpenBayanNext/apps/api/app/core/database.py)**:
   * Universal `libsql_client` wrapper with absolute file URI resolution and support for both in-process NVMe files and network/cloud Turso endpoints.

---

## 📊 Ingestion Summary & Database Footprint Breakdown

```text
========================================================================
🎉 Ingestion Summary (`data/shamela_corpus.db`)
========================================================================
   • Total Canonical Books:   60
   • Total Section Nodes:     97,533
   • Total Chunks / Pages:    76,274
   • Total Database File Size: 487.00 MB
   • FTS5 Rebuild Time:       6.26 seconds
   • Journal Mode:            DELETE (Read-Only Docker Safe)
========================================================================
```

### 💾 Physical Storage Footprint Analysis

The $487.00\text{ MB}$ single-file database footprint decomposes into two distinct storage layers:

| Component | Storage Size | % of Database | Description |
| :--- | :---: | :---: | :--- |
| **Dense Vector Embeddings** | **$234.3\text{ MB}$** | **$48.1\%$** | $76,274\text{ rows} \times 768\text{ dims} \times 4\text{ bytes}$ IEEE 754 float32 (`<f4`) blobs stored in `prepared_chunks.embedding`. |
| **Text, TOC & FTS5 Index** | **$252.7\text{ MB}$** | **$51.9\%$** | Full raw text, footnotes, bibliographic JSON, B-tree indexes, and SQLite FTS5 inverted posting lists (`prepared_chunks_fts`). |

---

## 🔍 Query Tokenization & Disjunctive Lemma Grouping

When converting user queries into SQLite FTS5 match expressions, attached prepositions (e.g. `بـ`, `لـ`, `كـ`, `فـ`) and morphological variants can prevent strict `AND` intersections from matching. 

> [!TIP]
> **Runtime Query Protocol (Milestone 2):**
> Runtime query generators must construct **disjunctive lemma groupings with mandatory root intersections**:
> ```text
> salient_roots_text: (عمل OR اعمال) AND (نوي OR نيه OR نيات OR بالنيات)
> ```
> This ensures queries like `إنما الأعمال بالنيات` match passages regardless of whether the word appears as `نية`, `نوى`, `النيات`, or `بالنيات`.

---

## 🧪 How to Test & Verify the Ingestion Results

We provide two dedicated testing tools located in [`dev_notes/01_milestone_1_ingestion_and_indexing/`](file:///home/abuhafi/Project/OpenBayanNext/dev_notes/01_milestone_1_ingestion_and_indexing/) to verify the corpus, query speeds, vector deserialization, and surrounding context.

### Method 1: Automated Verification Test Suite

Run the automated test script to verify SQLite journal mode, table counts, FTS5 BM25 queries, async `libsql_client` access, and vector deserialization latency:

```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/verify_milestone1.py
```

#### Actual Benchmark Output:
```text
================================================================================
🧪 1. Direct SQLite & FTS5 Verification
================================================================================
✓ Journal Mode: delete (Safe for Docker :ro mounts)
✓ Total Books:    60
✓ Total Sections: 97533
✓ Total Chunks:   76274

⚡ Benchmarking FTS5 BM25 Search Queries (JOIN Content Table):

  Query: 'سلم بيع' -> FTS Expr: 'salient_roots_text: (سلم AND بيع)'
  • Latency: 4.997 ms | Found Hits: 5
  • Top Hit: [صحيح البخاري - ن عطاءات العلم] | حديث: أن رسول الله أرخص لصاحب العرية (ج 2 ص 317) | BM25 Rank: -4.38
    Snippet: "٢١٨٨ - حدَّثنا عَبْدُ اللَّهِ بْنُ مَسْلَمَةَ: حدَّثنا مالِكٌ، عن نافِعٍ، عن ابْنِ عُمَرَ: عَنْ زَيْدِ بْنِ ثابِتٍ ﵃: أَ..."

  Query: 'صلاة وتر' -> FTS Expr: 'salient_roots_text: (صلاه AND وتر)'
  • Latency: 2.230 ms | Found Hits: 5
  • Top Hit: [رياض الصالحين - ت الفحل] | ٢١٢ - باب فضل قيام الليل (ص 332) | BM25 Rank: -8.23
    Snippet: "١١٦٨ - وعن ابن عمر ﵄: أنَّ النبيَّ ﷺ قَالَ: «صَلاةُ اللَّيْلِ مَثْنَى مَثْنَى، فَإذَا خِفْتَ الصُّبْحَ فَأوْتِرْ بِوَاحِ..."

  Query: 'طهارة ماء' -> FTS Expr: 'salient_roots_text: (طهاره AND ماء)'
  • Latency: 1.905 ms | Found Hits: 5
  • Top Hit: [عشرون حديثا من صحيح البخاري دراسة أسانيدها وشرح متونها] | المبحث الرابع: شرح الحديث (ص 71) | BM25 Rank: -7.99
    Snippet: "١٤- وجوب الإيمان بالمغيبات التي أخبر بها النبي ﷺ ماضيها كعدم حل الغنائم للماضين ومستقبلها كإعطائها ﷺ الشفاعة. ١٥- أنه لا..."

  Query: 'عقل قلب' -> FTS Expr: 'salient_roots_text: (عقل AND قلب)'
  • Latency: 1.764 ms | Found Hits: 5
  • Top Hit: [صحيح البخاري - ن عطاءات العلم] | حديث: أن رسول الله نهى عن المنابذة (ج 2 ص 304) | BM25 Rank: -7.44
    Snippet: "٢١٤٤ - حدَّثنا سَعِيدُ بْنُ عُفَيْرٍ، قالَ: حدَّثني اللَّيْثُ، قالَ: حدَّثني عُقَيْلٌ، عن ابْنِ شِهابٍ، قالَ: أخبَرَني ع..."

  Query: 'شفعة شريك' -> FTS Expr: 'salient_roots_text: (شفعه AND شريك)'
  • Latency: 0.506 ms | Found Hits: 5
  • Top Hit: [الحلل الإبريزية من التعليقات البازية على صحيح البخاري] | ٩٦ - باب بيع الشريك من شريكه (ج 2 ص 232) | BM25 Rank: -13.35
    Snippet: "قال الحافظ: ... قوله: (لا بأس العشرة بأحد عشرة) (١).  <span data-type="title" id=toc-978>٩٦ - باب بيع الشَّريك من شريكه<..."

================================================================================
🧪 2. Read-Only Immutable Access via libsql_client (FastAPI Driver)
================================================================================
✓ Async Count Query via libsql_client: 76274 rows (in 0.291 ms)
✓ Async FTS5 Search via libsql_client (in 0.521 ms) returned 3 rows:
  - [Chunk #161] [شرح العقيدة الطحاوية - عبد العزيز الراجحي] -> قوله: والشفاعة التي ادخرها لهم حق كما روي في الأخبار
  - [Chunk #362] [شرح العقيدة الطحاوية - عبد العزيز الراجحي] -> قوله: ونثبت الخلافة بعد رسول الله -صلى الله عليه وعلى آله وسلم- أولا لأبي بكر الصديق ﵁ تفضيلا له وتقديما على جميع الأمة ثم لعمر بن الخطاب ﵁ ثم لعثمان ﵁ ثم لعلي بن أبي طالب ﵁ وهم الخلفاء الرا
  - [Chunk #446] [مسائل العقيدة في كتاب التوحيد من صحيح البخاري] -> المطلب الخامس: شمائله
✓ Vector Blob Deserialization (50 candidate rows): 0.029 ms (NumPy frombuffer <f4)

🎉 ALL MILESTONE 1 VERIFICATIONS PASSED SUCCESSFULLY!
```

---

### Method 2: Interactive CLI Search & Diagnostics Tool

The [`dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py`](file:///home/abuhafi/Project/OpenBayanNext/dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py) tool provides a full-featured terminal interface.

#### 1. Single Term Search
```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py "شروط بيع السلم"
```
```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py "إنما الأعمال بالنيات"
```
```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py "صلاة الوتر في السفر"
```

#### Actual Query Output Example:
```text
════════════════════════════════════════════════════════════════════════════════
🔍 Search Query:  إنما الأعمال بالنيات
⚡ FTS5 Match:    salient_roots_text: (الاعمال AND اعمال AND عمل AND بالنيات)
⏱️ Execution:     3.554 ms | Total Results: 5
════════════════════════════════════════════════════════════════════════════════

[1] الحلل الإبريزية من التعليقات البازية على صحيح البخاري  (ج 1 ص 4)  [BM25 Rank: -20.57]
    📁 الحلل الإبريزية من التعليقات البازية على صحيح البخاري > تقريظ
    📖 يقول: سمعت عمر بن الخطاب ﵁ على المنبر، قال: سمعت رسول الله ﷺ يقول: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى، فمن كانت هجرته إلى دنيا يصيبها، أو إلى امرأة ينكحها، فهجرته إلى ما هاجر إليه».
    ────────────────────────────────────────────────────────────────────────────

[2] حديث إنما الأعمال بالنيات - من البدر المنير الساري في الكلام على صحيح البخاري  (ص 299)  [BM25 Rank: -20.41]
    📁 حديث إنما الأعمال بالنيات - من البدر المنير الساري في الكلام على صحيح البخاري > مقدمة الكتاب
    📖 من كتاب البدر المنير الساري في الكلام على صحيح البخاري (حديث إنما الأعمال بالنيات) تأليف أبي عليٍّ قُطْب الدِّين عبد الكَرِيم بن عبد النُّور بن مُنيِّر الحلبي (ت: ٧٣٥ هـ) تحقيق خالد عبد العظيم الحُوَيْني
```

#### 2. Interactive Search REPL
Launch an interactive search session:
```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py -i
```
Type any Arabic term or phrase and hit `Enter`. Type `exit` to quit.

#### 3. Level-2 Surrounding Context Inspector ($N-1 \leftrightarrow N+1$)
Inspect adjacent pages around any specific chunk ID:
```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py --context 72346
```

#### Actual Context Output:
```text
════════════════════════════════════════════════════════════════════════════════
📜 Level-2 Surrounding Context for Chunk #72346 in [تكملة السبكي على المجموع شرح المهذب - قطعة جديدة]
════════════════════════════════════════════════════════════════════════════════

   [Neighbor 828] Chunk #72345 | ج 2 ص 136 | Section: فصل [في فكاك الرهن]
   "وقولنا: "قدر حصته"، يعني به: مما يلزمهم أداؤه، فإن الدين قد يكون أكثر من التركة، وإنما يلزم مجموع الورثة أقل الأمرين من الدين وقيمة التركة.فرعلو استعار من رجلين ورهن من رجلين، فنصيب كلٍّ من المالكي..."

👉 [FOCUS HIT] Chunk #72346 | ج 2 ص 137 | Section: فصل [في فكاك الرهن]
   "فرعلو مات المرتهن عن ابنين، فوفى الراهن لأحدهما نصف الدين، قال ابن الرفعة: ها هنا يظهر أن يكون الصحيح أو المقطوع به: أن ينفك نصيبه من جهة أن الدين انتقل إليهما على السواء بالإرث، وعند انتقاله يجب أن ..."

   [Neighbor 830] Chunk #72347 | ج 2 ص 138 | Section: فصل [في فكاك الرهن]
   "فإن قلت: أنت قدمت أن بموت الراهن بعد القبض يتغير الحكم، ويصير مرهونًا بأقل الأمرين من الدين وقيمة التركة بعد ما كان مرهونًا بالدين عينًا.قلت: إذا كانت قيمة التركة أقل من الدين؛ فقد برئت ذمة الميت عن ..."
```

#### 4. Full Automated Benchmark Suite
Run queries across Fiqh, Hadith, Tafsir, and Aqeedah:
```bash
apps/api/.venv/bin/python dev_notes/01_milestone_1_ingestion_and_indexing/search_cli.py --test-suite
```

---

## 🚀 Next Steps: Milestone 2 (Hybrid Retrieval & Context Engine)

1. **FastAPI Hybrid Search Route (`/api/v1/search`)**: Combine FTS5 BM25 and CPU E5 vector cosine similarity using Reciprocal Rank Fusion (RRF).
2. **Contiguous Sibling Merger**: Automatically fuse adjacent page hits ($N, N+1$) from the same book into unified reading passages.
3. **3-Tier Context Resolvers**:
   * Level 1: Hit snippet (`/api/v1/chunks/{id}`)
   * Level 2: Surrounding context ($N-1 \leftrightarrow N+1$) respecting TOC boundaries (`/api/v1/chunks/{id}/surrounding`)
   * Level 3: Chapter stream (`/api/v1/books/{id}/sections/{sec_id}/chunks`)
