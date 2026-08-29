import { atom } from 'nanostores';

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
  window.addEventListener('popstate', (event) => {
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
