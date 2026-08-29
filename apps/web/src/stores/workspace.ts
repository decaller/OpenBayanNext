import { atom } from 'nanostores';
import type { SupportedLanguage } from '../lib/i18n';

export interface ActiveSectionState {
  bookId: number;
  sectionId: string;
  sectionTitle: string;
  breadcrumb: string;
  focusChunkId?: number;
}

export type FontSizeOption = 'sm' | 'base' | 'lg' | 'xl';
export type ContextDepth = 1 | 2;

export const $isDrawerOpen = atom<boolean>(false);
export const $activeSection = atom<ActiveSectionState | null>(null);
export const $fontSize = atom<FontSizeOption>('base');
export const $currentLang = atom<SupportedLanguage>('ar');
export const $toastMessage = atom<string | null>(null);

// Search Results Reading & Display Controls
export const $showHighlights = atom<boolean>(true);
export const $chunkFontSize = atom<FontSizeOption>('base');
export const $isCompact = atom<boolean>(false);
export const $contextDepth = atom<ContextDepth>(1);

export function showToast(message: string, durationMs: number = 3000) {
  $toastMessage.set(message);
  setTimeout(() => {
    if ($toastMessage.get() === message) {
      $toastMessage.set(null);
    }
  }, durationMs);
}

export function setLanguage(lang: SupportedLanguage) {
  $currentLang.set(lang);
  if (typeof window !== 'undefined') {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
  }
}

export function toggleHighlights() {
  const current = $showHighlights.get();
  $showHighlights.set(!current);
  updateDisplayClasses();
}

export function setChunkFontSize(size: FontSizeOption) {
  $chunkFontSize.set(size);
  updateDisplayClasses();
}

export function toggleCompactView() {
  const current = $isCompact.get();
  $isCompact.set(!current);
  updateDisplayClasses();
}

export function setContextDepth(depth: ContextDepth) {
  $contextDepth.set(depth);
  updateDisplayClasses();
}

function updateDisplayClasses() {
  if (typeof document === 'undefined') return;
  const container = document.getElementById('search-results-container');
  if (!container) return;

  // 1. Highlights
  if ($showHighlights.get()) {
    container.classList.remove('hide-highlights');
  } else {
    container.classList.add('hide-highlights');
  }

  // 2. Font Size
  container.classList.remove('chunk-font-sm', 'chunk-font-base', 'chunk-font-lg', 'chunk-font-xl');
  container.classList.add(`chunk-font-${$chunkFontSize.get()}`);

  // 3. Compact Density
  if ($isCompact.get()) {
    container.classList.add('compact-results');
  } else {
    container.classList.remove('compact-results');
  }

  // 4. Context Depth Level (1: Snippet, 2: Context ±1)
  container.classList.remove('depth-level-1', 'depth-level-2');
  container.classList.add(`depth-level-${$contextDepth.get()}`);
}

export function openChapterDrawer(section: ActiveSectionState) {
  $activeSection.set(section);
  $isDrawerOpen.set(true);

  if (typeof window !== 'undefined') {
    window.history.pushState({ drawerOpen: true }, '', window.location.href);
  }
}

export function closeChapterDrawer() {
  $isDrawerOpen.set(false);
}

// Global browser popstate & Escape key invariant
if (typeof window !== 'undefined') {
  window.addEventListener('popstate', () => {
    if ($isDrawerOpen.get()) {
      $isDrawerOpen.set(false);
    }
  });

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && $isDrawerOpen.get()) {
      $isDrawerOpen.set(false);
    }
  });
}
