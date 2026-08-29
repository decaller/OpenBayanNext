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
export type FontFamilyOption = 'amiri' | 'readex' | 'ibm-plex' | 'noto' | 'tajawal' | 'cairo';

// Load persisted settings from localStorage helper
function getStored<T>(key: string, defaultValue: T): T {
  if (typeof window === 'undefined') return defaultValue;
  try {
    const val = localStorage.getItem(key);
    if (val !== null) {
      return JSON.parse(val) as T;
    }
  } catch (e) {
    // Fallback to default
  }
  return defaultValue;
}

function setStored<T>(key: string, value: T) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    // Storage quota or disabled
  }
}

export const $isDrawerOpen = atom<boolean>(false);
export const $activeSection = atom<ActiveSectionState | null>(null);
export const $fontSize = atom<FontSizeOption>('base');
export const $currentLang = atom<SupportedLanguage>('ar');
export const $toastMessage = atom<string | null>(null);

// Search Results Reading & Display Controls (persisted in localStorage)
export const $showHighlights = atom<boolean>(getStored('openbayan_pref_highlights', true));
export const $chunkFontSize = atom<FontSizeOption>(getStored('openbayan_pref_fontsize', 'base'));
export const $isFontBold = atom<boolean>(getStored('openbayan_pref_fontbold', false));
export const $fontFamily = atom<FontFamilyOption>(getStored('openbayan_pref_fontfamily', 'amiri'));
export const $isCompact = atom<boolean>(getStored('openbayan_pref_compact', false));
export const $contextDepth = atom<ContextDepth>(getStored('openbayan_pref_depth', 1));

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
  const next = !$showHighlights.get();
  $showHighlights.set(next);
  setStored('openbayan_pref_highlights', next);
  updateDisplayClasses();
}

export function setChunkFontSize(size: FontSizeOption) {
  $chunkFontSize.set(size);
  setStored('openbayan_pref_fontsize', size);
  updateDisplayClasses();
}

export function toggleFontBold() {
  const next = !$isFontBold.get();
  $isFontBold.set(next);
  setStored('openbayan_pref_fontbold', next);
  updateDisplayClasses();
}

export function setFontFamily(family: FontFamilyOption) {
  $fontFamily.set(family);
  setStored('openbayan_pref_fontfamily', family);
  updateDisplayClasses();
}

export function toggleCompactView() {
  const next = !$isCompact.get();
  $isCompact.set(next);
  setStored('openbayan_pref_compact', next);
  updateDisplayClasses();
}

export function setContextDepth(depth: ContextDepth) {
  $contextDepth.set(depth);
  setStored('openbayan_pref_depth', depth);
  updateDisplayClasses();
}

export function updateDisplayClasses() {
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

  // 3. Arabic Font-Family
  container.classList.remove(
    'font-family-amiri',
    'font-family-readex',
    'font-family-ibm-plex',
    'font-family-noto',
    'font-family-tajawal',
    'font-family-cairo'
  );
  container.classList.add(`font-family-${$fontFamily.get()}`);

  // 4. Arabic Font Weight Bold
  if ($isFontBold.get()) {
    container.classList.add('matn-bold');
  } else {
    container.classList.remove('matn-bold');
  }

  // 5. Compact Density
  if ($isCompact.get()) {
    container.classList.add('compact-results');
  } else {
    container.classList.remove('compact-results');
  }

  // 6. Context Depth Level (1: Snippet, 2: Context ±1)
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

// Global browser listeners and initial settings sync
if (typeof window !== 'undefined') {
  // Sync display classes on initial page load
  window.addEventListener('DOMContentLoaded', () => {
    updateDisplayClasses();
  });
  // Execute immediately if DOM already loaded
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    updateDisplayClasses();
  }

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
