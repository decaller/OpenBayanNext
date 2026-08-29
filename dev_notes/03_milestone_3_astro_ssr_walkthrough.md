# Milestone 3: Astro SSR & DaisyUI Reader Islands — Complete Walkthrough

This document records the complete frontend architecture, 0-JS SSR permalinks, Nanostores state bridge, and verification benchmarks for **Milestone 3**.

---

## 🎯 Architecture & User Flows

```
                          ASTRO SSR & REACT ISLANDS ARCHITECTURE
                          
    User / Web Crawler (Googlebot, User Browser)
        │
        ├──► `GET /p/:id` (0-JS SSR Permalink)
        │       • Zero client JavaScript bundle on initial page load (0 KB JS)
        │       • Schema.org `ScholarlyArticle` JSON-LD metadata in `<head>`
        │       • Pre-rendered Level-2 surrounding context ($N \pm 1$) with boundary indicators
        │
        ├──► `GET /search?q=...&page=1` (SSR Search Page)
        │       • SSR-rendered results for instant crawler indexing & sub-40ms rendering
        │       • `<SearchBar client:load/>` debounced search island with keyboard shortcuts
        │       • Static `<PassageCard.astro/>` with `data-open-drawer` bridge (0 KB JS per card)
        │       • Server-rendered pagination controls (`/search?q=...&page=2`)
        │
        └──► `<CitationDrawer client:idle/>` (React Island)
                • Subscribed to Nanostores (`$isDrawerOpen`, `$activeSection`, `$fontSize`)
                • Slide-out RTL chapter reader fetching continuous chunk stream
                • History pushState & popstate management (Back button closes drawer)
                • Font resizing (A- / A+), copy citation button, auto-scroll to focus chunk
```

---

## 📁 Implemented Modules & Components

1. **Dual API URL Resolution ([`api.ts`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/lib/api.ts))**:
   * Resolves `INTERNAL_API_URL` (`http://127.0.0.1:8001/api/v1`) for server-side `.astro` frontmatter.
   * Resolves `PUBLIC_API_URL` (`http://127.0.0.1:8001/api/v1` or `/api/v1`) for client-side React islands.

2. **Typography & Design System ([`app.css`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/assets/app.css))**:
   * Bundled self-hosted `@fontsource/amiri` (for classical Arabic matn) and `@fontsource/ibm-plex-sans-arabic` (for modern UI labels).
   * Arabic line-height `2.3` (`leading-loose`) to prevent Tashkeel diacritic collisions.
   * Visual page divider (`.page-divider`) for merged adjacent sibling passages.

3. **Nanostores State & History Bridge ([`workspace.ts`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/stores/workspace.ts))**:
   * Manages drawer open state, active chapter section, and font size.
   * Integrates `window.history.pushState` and `popstate` so browser Back and `Escape` key close the drawer smoothly.

4. **Global Layout & Island Bridge ([`BaseLayout.astro`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/layouts/BaseLayout.astro))**:
   * RTL HTML boilerplate with OpenGraph meta tags.
   * Single global delegated click listener for `[data-open-drawer]` that updates Nanostores directly, avoiding 20 redundant React micro-islands.

5. **0-JS SEO Permalink Page ([`src/pages/p/[id].astro`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/pages/p/[id].astro))**:
   * Server-side fetches Level-1 detail and Level-2 surrounding context.
   * Generates Schema.org `ScholarlyArticle` JSON-LD.
   * Pre-renders $N \pm 1$ neighbor passages with cross-chapter boundary badges.

6. **SSR Search Page ([`src/pages/search.astro`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/pages/search.astro))**:
   * Server-renders search hits from `/api/v1/search`.
   * Displays merged page ranges (`ج 1 ص 526 - 527`), RRF relevance scores, and server-side pagination links.

7. **Slide-Out Chapter Reader Drawer ([`CitationDrawer.tsx`](file:///home/abuhafi/Project/OpenBayanNext/apps/web/src/components/islands/CitationDrawer.tsx))**:
   * React island streaming continuous chapter chunks from `/api/v1/books/{id}/sections/{sec_id}/chunks`.
   * Auto-scrolls to the target focus chunk, provides font size toggles, and one-click citation copying.

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
✓ Homepage rendered successfully (14453 bytes, status 200)

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

## 🚀 Next Steps: Milestone 4 (Container Gateway & Production Orchestration)

1. **Docker Compose & Gateway Architecture (`compose.yml`)**:
   * Containerize FastAPI Backend (`apps/api/Dockerfile`) and Astro SSR Node (`apps/web/Dockerfile`).
   * Configure Zoraxy reverse proxy gateway for unified routing (`/` to frontend, `/api/v1` to backend).
2. **Production Validation**:
   * Verify read-only database volume mounts (`./data/shamela_corpus.db:/data/shamela_corpus.db:ro`).
   * Confirm crawler indexability and end-to-end response speeds.
