import React from 'react';
import { useStore } from '@nanostores/react';
import { 
  $showHighlights, 
  $chunkFontSize, 
  $isCompact,
  $contextDepth,
  $currentLang,
  toggleHighlights, 
  setChunkFontSize, 
  toggleCompactView,
  setContextDepth,
  type FontSizeOption,
  type ContextDepth
} from '../../stores/workspace';
import { translations, type SupportedLanguage } from '../../lib/i18n';

interface SearchControlsProps {
  lang?: SupportedLanguage;
}

export const SearchControls: React.FC<SearchControlsProps> = ({ lang: initialLang }) => {
  const showHighlights = useStore($showHighlights);
  const fontSize = useStore($chunkFontSize);
  const isCompact = useStore($isCompact);
  const contextDepth = useStore($contextDepth);
  const storeLang = useStore($currentLang);
  const currentLang = initialLang || storeLang || 'ar';
  const t = translations[currentLang] || translations.ar;

  const fontOptions: { id: FontSizeOption; label: string }[] = [
    { id: 'sm', label: 'A-' },
    { id: 'base', label: 'A' },
    { id: 'lg', label: 'A+' },
    { id: 'xl', label: 'A++' },
  ];

  const depthOptions: { id: ContextDepth; label: string }[] = [
    { id: 1, label: t.depthLevel1 },
    { id: 2, label: t.depthLevel2 },
  ];

  return (
    <div className="bg-base-100 border border-base-200 rounded-2xl p-4 shadow-sm space-y-3.5 font-sans text-xs">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-base-200/60 font-bold text-base-content">
        <div className="flex items-center gap-1.5">
          <svg className="w-4 h-4 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <span>{t.displayControlsTitle}</span>
        </div>
      </div>

      <div className="space-y-3 pt-0.5">
        {/* 1. Context Depth Switcher (2 Levels: 1: Snippet, 2: Context ±1) */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-base-content/70 font-semibold">{t.depthLevelLabel}</span>
            <span className="text-[10px] font-mono text-emerald-700 dark:text-emerald-400 font-bold">
              {contextDepth === 1 ? 'Atomic' : 'Discourse ±1'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 bg-base-200/80 p-1 rounded-xl">
            {depthOptions.map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setContextDepth(opt.id)}
                className={`btn btn-xs rounded-lg border-0 transition-all font-sans ${
                  contextDepth === opt.id 
                    ? 'bg-emerald-800 text-white font-bold shadow-xs' 
                    : 'btn-ghost text-base-content/70 hover:text-base-content'
                }`}
              >
                <span className="truncate">{opt.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 2. Font Size Control */}
        <div className="flex items-center justify-between pt-1 border-t border-base-200/50">
          <span className="text-base-content/70 font-semibold">{t.fontSizeLabel}</span>
          <div className="join bg-base-200/80 rounded-lg p-0.5">
            {fontOptions.map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setChunkFontSize(opt.id)}
                className={`join-item btn btn-xs ${fontSize === opt.id ? 'btn-active bg-emerald-800 text-white font-bold' : 'btn-ghost'}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* 3. Highlights Toggle */}
        <div className="flex items-center justify-between pt-1 border-t border-base-200/50">
          <span className="text-base-content/70 font-semibold">{t.highlightToggleLabel}</span>
          <button
            type="button"
            onClick={toggleHighlights}
            className={`btn btn-xs rounded-lg transition-colors gap-1 ${
              showHighlights 
                ? 'btn-success bg-emerald-700 text-white border-0 hover:bg-emerald-800' 
                : 'btn-outline btn-neutral opacity-60'
            }`}
          >
            {showHighlights ? (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>{t.toggleOn}</span>
              </>
            ) : (
              <span>{t.toggleOff}</span>
            )}
          </button>
        </div>

        {/* 4. Card Density Toggle */}
        <div className="flex items-center justify-between pt-1 border-t border-base-200/50">
          <span className="text-base-content/70 font-semibold">{t.densityLabel}</span>
          <button
            type="button"
            onClick={toggleCompactView}
            className={`btn btn-xs rounded-lg transition-colors ${
              isCompact 
                ? 'btn-active bg-stone-800 text-white font-bold' 
                : 'btn-ghost border border-base-300'
            }`}
          >
            {isCompact ? t.densityCompact : t.densityNormal}
          </button>
        </div>
      </div>
    </div>
  );
};
