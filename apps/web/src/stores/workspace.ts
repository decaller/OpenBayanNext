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

export const $isDrawerOpen = atom<boolean>(false);
export const $activeSection = atom<ActiveSectionState | null>(null);
export const $fontSize = atom<FontSizeOption>('base');
export const $currentLang = atom<SupportedLanguage>('ar');
export const $toastMessage = atom<string | null>(null);

export function showToast(message: string, durationMs: number = 3000) {
  $toastMessage.set(message);
  setTimeout(() => {
    if ($toastMessage.get() === message) {
      $toastMessage.set(null);
    }
  }, durationMs);
}

/**
 * Changes language and updates URL query param
 */
export function setLanguage(lang: SupportedLanguage) {
  $currentLang.set(lang);
  if (typeof window !== 'undefined') {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
  }
}

/**
 * Opens the Chapter Reader Drawer and binds browser history (pushState)
 * so that the user's Back button closes the drawer instead of navigating away.
 */
export function openChapterDrawer(section: ActiveSectionState) {
  $activeSection.set(section);
  $isDrawerOpen.set(true);

  if (typeof window !== 'undefined') {
    window.history.pushState({ drawerOpen: true }, '', window.location.href);
  }
}

/**
 * Closes the Chapter Reader Drawer cleanly.
 */
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
