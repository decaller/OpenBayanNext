# Milestone 3: Astro SSR & DaisyUI Reader Islands — Complete Walkthrough

This document records the complete frontend architecture, 0-JS SSR permalinks, Nanostores state bridge, verification benchmarks, 4 high-value research features, trilingual i18n support, **Contiguous Sibling Merging**, **Thematic SIMD Clustering**, **Accuracy-Ranked Theme Partitioning**, accurate passage counters, scrollable sidebar navigation, 2-Level Context Depth Switcher, Thematic Top-5 Capping with Direct Topic Search, **Unified Full Candidate Retrieval (Zero-Pagination Architecture)**, and dynamic bidirectional chunk streaming for **Milestone 3**.

---

## 🎯 Architecture & User Flows

```
                     TRILINGUAL i18n & SCHOLARLY AI RESEARCH WORKSPACE
                     
    User / Web Crawler (?lang=ar | ?lang=en | ?lang=id)
        │
        ├──► `GET /p/:id` (0-JS SSR Permalink)
        │       • Zero client JavaScript bundle on initial page load (0 KB JS)
        │       • Schema.org `ScholarlyArticle` JSON-LD metadata in `<head>`
        │       • Pre-rendered Level-2 surrounding context ($N \pm 1$) with boundary indicators
        │       • "Copy for AI" prompt generator & external edition links (Turath / Shamela)
        │
        ├──► `GET /search?q=...` (Unified Thematic SSR Search Workspace - Zero Pagination)
        │       • Layer 1: Contiguous Sibling Merging (Physical Sequence Fusion with 1.05x Score Multiplier)
        │       • Layer 2: Thematic SIMD Clustering (Ranked strictly by whole-sentence query accuracy descending)
        │       • Query Sentence Accuracy: Full sentence Jaccard & Vector similarity (e.g. 92% -> 89% -> 74%)
        │       • Complete Candidate Delivery: All candidate hits returned in a single high-performance payload
        │       • Accurate Passage Counters: Displays full count found (`N passages`) with top-5 capping per theme
        │       • Direct Thematic Deep Search: [بحث مستقل في هذا المحور ↗]
        │       • 2-Level Context Depth Switcher:
        │           - Level 1 [Snippet / مقتطف]: Single focused matched passage
        │           - Level 2 [Context (±1) / سياق]: 3-Block Triad (Preceding N-1, Target Focus, Succeeding N+1)
        │       • Sticky Floating Sidebar:
        │           1. Scrollable Thematic Structure List (With % query accuracy badge per theme item)
        │           2. Simplified AI Card ([Full Data] & [Page URL] side-by-side)
        │           3. <SearchControls client:load/> (2-Level Depth, Font sizing & Highlights toggle)
        │
        └──► `<CitationDrawer client:idle/>` (React Island)
                • Subscribed to Nanostores (`$isDrawerOpen`, `$activeSection`, `$fontSize`, `$currentLang`, `$contextDepth`)
                • Slide-out RTL chapter reader fetching continuous chunk stream
                • Bidirectional Chunk Expansion:
                    - [⌃ Load Earlier Passages (N-3, N-4...)]
                    - [⌄ Load Subsequent Passages (N+3, N+4...)]
                • Fully localized headers (`الموضع المعتمد: #...`, `مسار الباب والتصنيف:`, `الموضع المطابق`)
                • Clean light-paper theme styling (`bg-emerald-50` focus background)
                • History pushState & popstate management (Back button closes drawer)
                • Font resizing (A- / A+), copy citation button, auto-scroll to focus chunk
```

---

## 📁 Accuracy-Ranked Theme Partitioning

* **Ranking Rule ([`thematic_clusterer.ts`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/lib/thematic_clusterer.ts))**:
  * Clusters are dynamically sorted in **descending order of query sentence match accuracy** ($92\% \rightarrow 89\% \rightarrow 74\% \dots$).
  * The most relevant theme to the full user sentence query is guaranteed to appear as **Thematic Group #1** at the top of the feed and at the top of the sidebar navigation.
  * Secondary tie-breaker is total passage density (`doc_count`).

---

## 🧪 Verification & Benchmark Results

Run the verification suite:
```bash
apps/api/.venv/bin/python dev_notes/03_milestone_3_astro_ssr/verify_milestone3.py
```

### Actual Output:
```text
================================================================================
🚀 OPENBAYAN MILESTONE 3: ASTRO SSR & DAISYUI READER VERIFICATION SUITE
================================================================================

[Step 1/5] Starting FastAPI Backend on port 8001...
✓ FastAPI Backend healthy & responsive on http://127.0.0.1:8001

[Step 2/5] Starting Astro SSR Node Server on port 4321...
✓ Astro SSR Server healthy & responsive on http://127.0.0.1:4321

[Step 3/5] Testing Homepage (GET /)...
✓ Homepage rendered successfully (16116 bytes, status 200)

[Step 4/5] Testing SSR Search Page (GET /search?q=شروط+بيع+السلم)...
✓ Search page server-rendered in 40.76 ms (63634 bytes, status 200)
  • Verified pre-rendered Arabic text & data-open-drawer attributes.

[Step 5/5] Testing 0-JS Permalink Page (GET /p/72346)...
✓ 0-JS Permalink page server-rendered in 17.52 ms (17797 bytes, status 200)
  • Verified Schema.org ScholarlyArticle JSON-LD.
  • Verified Pre-rendered Level-2 ($N ± 1$) surrounding context.
  • Verified 0-JS static semantic HTML.

================================================================================
🎉 ALL MILESTONE 3 SSR & UI VERIFICATIONS PASSED SUCCESSFULLY!
================================================================================
```
