# Milestone 3: Astro SSR & DaisyUI Reader Islands — Complete Walkthrough

This document records the complete frontend architecture, 0-JS SSR permalinks, Nanostores state bridge, verification benchmarks, 4 high-value research features, and trilingual i18n support for **Milestone 3**.

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
        ├──► `GET /search?q=...&page=1` (SSR Search Page)
        │       • SSR-rendered results for instant crawler indexing & sub-40ms rendering
        │       • `<SearchBar client:load/>` debounced search island with keyboard shortcuts
        │       • Static `<PassageCard.astro/>` with `data-open-drawer` bridge (0 KB JS per card)
        │       • Keyword & root highlighting (`<mark class="bg-emerald-100...">`)
        │       • Sticky Telemetry & "Explore with Your Own AI" Sidebar
        │       • Server-rendered pagination controls (`/search?q=...&page=2`)
        │
        └──► `<CitationDrawer client:idle/>` (React Island)
                • Subscribed to Nanostores (`$isDrawerOpen`, `$activeSection`, `$fontSize`, `$currentLang`)
                • Slide-out RTL chapter reader fetching continuous chunk stream
                • History pushState & popstate management (Back button closes drawer)
                • Font resizing (A- / A+), copy citation button, auto-scroll to focus chunk
```

---

## 📁 Implemented Modules & Components

1. **Trilingual i18n System ([`i18n.ts`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/lib/i18n.ts))**:
   * Complete dictionary for **العربية (ar)**, **English (en)**, and **Bahasa Indonesia (id)**.
   * Dynamic direction switching (`dir="rtl"` for Arabic, `dir="ltr"` for English/Indonesian while keeping classical Arabic matn strictly in RTL `font-amiri`).
   * Standardized AI Prompt generation tailored per language.

2. **Language Switcher Island ([`LanguageSwitcher.tsx`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/components/islands/LanguageSwitcher.tsx))**:
   * Dropdown in Header allowing instant language switching (`🇸🇦 العربية`, `🇬🇧 English`, `🇮🇩 Indonesia`).

3. **Keyword & Root Highlighter ([`highlighter.ts`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/lib/highlighter.ts))**:
   * Wraps search query tokens and stems in soft emerald `<mark>` tags.

4. **Dual API URL Resolution ([`api.ts`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/lib/api.ts))**:
   * Resolves `INTERNAL_API_URL` (`http://127.0.0.1:8001/api/v1`) for server-side `.astro` frontmatter.
   * Resolves `PUBLIC_API_URL` (`http://127.0.0.1:8001/api/v1` or `/api/v1`) for client-side React islands.

5. **Passage Card & AI Prompt Bridge ([`PassageCard.astro`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/components/astro/PassageCard.astro))**:
   * Renders merged page ranges (`ج 1 ص 526 - 527`), external links to **Turath.io ↗** and **Shamela.ws ↗**, and **"Copy for AI"** button.

6. **Search Page & AI Grounding Sidebar ([`search.astro`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/pages/search.astro))**:
   * Main 8-column results list + 4-column sticky sidebar with performance telemetry, unique book anchors, and a copyable page URL prompt.

7. **Slide-Out Chapter Reader Drawer ([`CitationDrawer.tsx`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/components/islands/CitationDrawer.tsx))**:
   * Streaming multi-page chapter reader with external digital edition links and copy citation cards.

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

---

## 🖥️ Manual Browser Verification Scenarios

Both the **Astro SSR Web Application** and the **FastAPI Backend** are running live:

* 🌐 **Web Interface:** [http://localhost:4321](http://localhost:4321)
* ⚡ **API Swagger UI:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

### 1. 🌐 Trilingual Language Switching (AR / EN / ID)
* Click the language selector at the top right of the navbar to switch between **🇸🇦 العربية**, **🇬🇧 English**, and **🇮🇩 Bahasa Indonesia**.
* Notice how UI labels switch gracefully (e.g. `Search Mode` / `Mode Pencarian`, `Copy for AI` / `Salin untuk AI`), while classical Arabic matn remains in pristine RTL `font-amiri` typography.

### 2. 🤖 "Copy for AI" Structured Prompt
* Click **[Copy for AI]** or **[نسخ للذكاء الاصطناعي]** on any search card.
* Paste it into your notes or ChatGPT/Claude $\to$ it generates a structured prompt with book title, author, volume/page, canonical permalink, and analytical instructions!

### 3. 🔗 External Library Verification (`Turath.io ↗` & `Shamela.ws ↗`)
* Notice the **[Turath.io ↗]** and **[Shamela.ws ↗]** buttons on every card and in the chapter drawer.

### 4. 🎨 Keyword & Root Highlighting
* Search for `شروط بيع السلم` $\to$ observe query terms and roots visually highlighted in soft emerald `<mark>` tags.

### 5. 📊 Sticky Search Telemetry & AI Grounding Sidebar
* In search results, inspect the right-side sticky panel:
  * Shows execution latency and hybrid retrieval mode.
  * Shows unique book outline.
  * Click **[Copy Page URL for AI]** to copy the full-page exploration prompt.

---

## 🚀 Next Steps: Milestone 4 (Container Gateway & Production Orchestration)

1. **Docker Compose & Gateway Architecture (`compose.yml`)**:
   * Containerize FastAPI Backend (`apps/api/Dockerfile`) and Astro SSR Node (`apps/web/Dockerfile`).
   * Configure Zoraxy reverse proxy gateway for unified routing (`/` to frontend, `/api/v1` to backend).
2. **Production Validation**:
   * Verify read-only database volume mounts (`./data/shamela_corpus.db:/data/shamela_corpus.db:ro`).
   * Confirm crawler indexability and end-to-end response speeds.
