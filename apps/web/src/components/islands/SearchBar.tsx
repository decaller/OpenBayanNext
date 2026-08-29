import React, { useState, useEffect, useRef } from 'react';
import { translations, type SupportedLanguage } from '../../lib/i18n';

interface SearchBarProps {
  initialQuery?: string;
  initialMode?: 'hybrid' | 'fts' | 'vector';
  size?: 'normal' | 'large';
  autoFocus?: boolean;
  lang?: SupportedLanguage;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  initialQuery = '',
  initialMode = 'hybrid',
  size = 'normal',
  autoFocus = false,
  lang = 'ar',
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [mode, setMode] = useState<'hybrid' | 'fts' | 'vector'>(initialMode);
  const inputRef = useRef<HTMLInputElement>(null);
  const t = translations[lang] || translations.ar;

  useEffect(() => {
    // Keyboard shortcut '/' to focus search bar
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    const url = `/search?q=${encodeURIComponent(query.trim())}&mode=${mode}&page=1&lang=${lang}`;
    window.location.href = url;
  };

  const isLarge = size === 'large';

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto font-sans">
      <div className={`relative flex items-center bg-base-100 rounded-2xl border-2 border-emerald-800/20 focus-within:border-emerald-700 shadow-sm transition-all ${isLarge ? 'p-2 sm:p-2.5' : 'p-1.5'}`}>
        {/* Search Icon */}
        <div className="pl-3 pr-2 text-emerald-800/60 flex items-center">
          <svg className={isLarge ? "w-6 h-6" : "w-5 h-5"} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* Input Field */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t.searchPlaceholder}
          autoFocus={autoFocus}
          className={`w-full bg-transparent outline-none font-sans text-base-content placeholder:text-base-content/40 ${isLarge ? 'text-base sm:text-lg py-2' : 'text-sm sm:text-base py-1'}`}
        />

        {/* Clear button if query exists */}
        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="btn btn-ghost btn-circle btn-xs text-base-content/50 ml-1"
          >
            ✕
          </button>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className={`btn btn-emerald bg-emerald-800 hover:bg-emerald-900 text-white font-bold rounded-xl mx-2 ${isLarge ? 'px-6 btn-md' : 'px-4 btn-sm'}`}
        >
          {t.searchBtn}
        </button>
      </div>

      {/* Mode Selector Pills */}
      <div className="flex items-center justify-between mt-2.5 px-2 text-xs text-base-content/60">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-semibold text-base-content/70">{t.searchType}</span>
          <div className="join bg-base-200/60 p-0.5 rounded-lg border border-base-300/40">
            <button
              type="button"
              onClick={() => setMode('hybrid')}
              className={`join-item btn btn-xs border-0 ${mode === 'hybrid' ? 'btn-active bg-emerald-800 text-white font-bold' : 'btn-ghost'}`}
            >
              {t.modeHybrid}
            </button>
            <button
              type="button"
              onClick={() => setMode('fts')}
              className={`join-item btn btn-xs border-0 ${mode === 'fts' ? 'btn-active bg-emerald-800 text-white font-bold' : 'btn-ghost'}`}
            >
              {t.modeFts}
            </button>
            <button
              type="button"
              onClick={() => setMode('vector')}
              className={`join-item btn btn-xs border-0 ${mode === 'vector' ? 'btn-active bg-emerald-800 text-white font-bold' : 'btn-ghost'}`}
            >
              {t.modeVector}
            </button>
          </div>
        </div>

        <span className="hidden sm:inline-block text-[11px] opacity-70">
          {t.pressSlash}
        </span>
      </div>
    </form>
  );
};
