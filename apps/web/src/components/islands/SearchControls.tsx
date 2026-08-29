import React, { useState, useEffect } from 'react';
import { useStore } from '@nanostores/react';
import { 
  $showHighlights, 
  $chunkFontSize, 
  $isFontBold,
  $fontFamily,
  $isCompact,
  $contextDepth,
  $currentLang,
  setLanguage,
  toggleHighlights, 
  setChunkFontSize, 
  toggleFontBold,
  setFontFamily,
  toggleCompactView,
  setContextDepth,
  type FontSizeOption,
  type FontFamilyOption,
  type ContextDepth
} from '../../stores/workspace';
import { translations, type SupportedLanguage } from '../../lib/i18n';

interface SearchControlsProps {
  lang?: SupportedLanguage;
}

const THEMES = [
  { id: 'emerald', name: 'Emerald', labelAr: 'زمردي', icon: '🌿' },
  { id: 'retro', name: 'Retro', labelAr: 'مخطوطة', icon: '📜' },
  { id: 'light', name: 'Light', labelAr: 'فاتح', icon: '☀️' },
  { id: 'dark', name: 'Dark', labelAr: 'داكن', icon: '🌙' },
  { id: 'night', name: 'Night', labelAr: 'ليلي', icon: '🌌' },
  { id: 'corporate', name: 'Corporate', labelAr: 'أكاديمي', icon: '🏛️' },
  { id: 'winter', name: 'Winter', labelAr: 'شتوي', icon: '❄️' },
  { id: 'coffee', name: 'Coffee', labelAr: 'قهوة', icon: '☕' },
];

const LANGUAGES: { code: SupportedLanguage; label: string; flag: string }[] = [
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'id', label: 'Indonesia', flag: '🇮🇩' },
];

const FONTS: { id: FontFamilyOption; name: string; labelAr: string; type: string }[] = [
  { id: 'amiri', name: 'Amiri', labelAr: 'أميري', type: 'نسخ تراثي' },
  { id: 'readex', name: 'Readex', labelAr: 'ريدكس', type: 'حديث واضح' },
  { id: 'ibm-plex', name: 'IBM Plex', labelAr: 'بلكس', type: 'متوازن' },
  { id: 'noto', name: 'Noto', labelAr: 'نوتو', type: 'قياسي' },
  { id: 'tajawal', name: 'Tajawal', labelAr: 'تجوال', type: 'عصري' },
  { id: 'cairo', name: 'Cairo', labelAr: 'كايرو', type: 'هندسي' },
];

export const SearchControls: React.FC<SearchControlsProps> = ({ lang: initialLang }) => {
  const showHighlights = useStore($showHighlights);
  const fontSize = useStore($chunkFontSize);
  const isFontBold = useStore($isFontBold);
  const currentFontFamily = useStore($fontFamily);
  const isCompact = useStore($isCompact);
  const contextDepth = useStore($contextDepth);
  const storeLang = useStore($currentLang);
  const currentLang = initialLang || storeLang || 'ar';
  const t = translations[currentLang] || translations.ar;

  const [isOpen, setIsOpen] = useState(true);
  const [currentTheme, setCurrentTheme] = useState('emerald');

  // Initialize and persist collapse state and active theme in localStorage
  useEffect(() => {
    try {
      const savedCard = localStorage.getItem('openbayan_card_controls_open');
      if (savedCard !== null) {
        setIsOpen(JSON.parse(savedCard));
      }
      const savedTheme = localStorage.getItem('openbayan_theme') || 'emerald';
      setCurrentTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } catch (e) {}
  }, []);

  const toggleOpen = () => {
    const next = !isOpen;
    setIsOpen(next);
    try {
      localStorage.setItem('openbayan_card_controls_open', JSON.stringify(next));
    } catch (e) {}
  };

  const handleThemeChange = (themeId: string) => {
    setCurrentTheme(themeId);
    document.documentElement.setAttribute('data-theme', themeId);
    try {
      localStorage.setItem('openbayan_theme', themeId);
    } catch (e) {}
  };

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
    <div className="bg-base-100 border border-base-200 rounded-2xl p-4 shadow-sm space-y-3 font-sans text-xs transition-all">
      {/* Clickable Collapse Header */}
      <button 
        type="button"
        onClick={toggleOpen}
        className="flex items-center justify-between w-full font-bold text-base-content hover:text-primary transition-colors text-start focus:outline-none"
        title={isOpen ? 'Collapse' : 'Expand'}
      >
        <div className="flex items-center gap-1.5">
          <svg className="w-4 h-4 text-emerald-700 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <span>{t.displayControlsTitle}</span>
        </div>

        {/* Collapse Indicator Chevron */}
        <span className={`w-5 h-5 flex items-center justify-center rounded-md bg-base-200 text-base-content/60 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>

      {/* Collapsible Content Body */}
      {isOpen && (
        <div className="space-y-3.5 pt-2 border-t border-base-200/60">
          
          {/* 1. Theme Controller Grid */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-base-content/70 font-semibold flex items-center gap-1">
                <svg className="w-3.5 h-3.5 text-emerald-700 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                <span>السمة / Theme</span>
              </span>
              <span className="text-[10px] font-mono text-primary font-bold capitalize">
                {currentTheme}
              </span>
            </div>
            
            <div className="grid grid-cols-4 gap-1">
              {THEMES.map((th) => {
                const isSelected = currentTheme === th.id;
                return (
                  <button
                    key={th.id}
                    type="button"
                    onClick={() => handleThemeChange(th.id)}
                    className={`btn btn-xs rounded-lg transition-all flex flex-col h-auto py-1 px-0.5 gap-0.5 border ${
                      isSelected
                        ? 'btn-primary font-bold shadow-xs'
                        : 'bg-base-200/80 hover:bg-base-200 text-base-content/80 border-base-200'
                    }`}
                    title={th.labelAr}
                  >
                    <span className="text-xs leading-none">{th.icon}</span>
                    <span className="text-[9px] truncate w-full">{th.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Interface Language Switcher */}
          <div className="space-y-1.5 pt-1.5 border-t border-base-200/50">
            <div className="flex items-center justify-between">
              <span className="text-base-content/70 font-semibold flex items-center gap-1">
                <svg className="w-3.5 h-3.5 text-emerald-700 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
                <span>اللغة / Language</span>
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-1 bg-base-200/80 p-1 rounded-xl">
              {LANGUAGES.map((l) => {
                const isSelected = currentLang === l.code;
                return (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => setLanguage(l.code)}
                    className={`btn btn-xs rounded-lg border-0 transition-all font-sans gap-1 ${
                      isSelected 
                        ? 'btn-primary font-bold shadow-xs' 
                        : 'btn-ghost text-base-content/70 hover:text-base-content'
                    }`}
                  >
                    <span>{l.flag}</span>
                    <span className="truncate">{l.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 3. Arabic Typeface / Font Family Selector */}
          <div className="space-y-1.5 pt-1.5 border-t border-base-200/50">
            <div className="flex items-center justify-between">
              <span className="text-base-content/70 font-semibold flex items-center gap-1">
                <svg className="w-3.5 h-3.5 text-emerald-700 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
                <span>{t.fontFamilyLabel}</span>
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-1">
              {FONTS.map((f) => {
                const isSelected = currentFontFamily === f.id;
                return (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => setFontFamily(f.id)}
                    className={`btn btn-xs rounded-lg transition-all flex flex-col h-auto py-1 px-1 gap-0.5 border text-start ${
                      isSelected 
                        ? 'btn-primary font-bold shadow-xs' 
                        : 'bg-base-200/80 hover:bg-base-200 text-base-content/80 border-base-200'
                    }`}
                  >
                    <span className="font-bold text-[11px] leading-tight truncate w-full">{f.name}</span>
                    <span className="text-[9px] opacity-70 truncate w-full">{f.type}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 4. Font Size & Arabic Bold Toggle */}
          <div className="flex items-center justify-between pt-1.5 border-t border-base-200/50 gap-2">
            <div>
              <span className="text-base-content/70 font-semibold block text-[11px] mb-1">{t.fontSizeLabel}</span>
              <div className="join bg-base-200/80 rounded-lg p-0.5">
                {fontOptions.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setChunkFontSize(opt.id)}
                    className={`join-item btn btn-xs ${fontSize === opt.id ? 'btn-active btn-primary font-bold' : 'btn-ghost'}`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <span className="text-base-content/70 font-semibold block text-[11px] mb-1">{t.fontBoldLabel}</span>
              <button
                type="button"
                onClick={toggleFontBold}
                className={`btn btn-xs rounded-lg transition-colors gap-1 ${
                  isFontBold 
                    ? 'btn-primary font-bold shadow-xs' 
                    : 'btn-ghost border border-base-300'
                }`}
              >
                <span className="font-bold text-xs">B</span>
                <span>{isFontBold ? t.toggleOn : t.toggleOff}</span>
              </button>
            </div>
          </div>

          {/* 5. Context Depth Switcher (2 Levels: 1: Snippet, 2: Context ±1) */}
          <div className="space-y-1.5 pt-1.5 border-t border-base-200/50">
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
                      ? 'btn-primary font-bold shadow-xs' 
                      : 'btn-ghost text-base-content/70 hover:text-base-content'
                  }`}
                >
                  <span className="truncate">{opt.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 6. Highlights Toggle & Card Density Toggle */}
          <div className="grid grid-cols-2 gap-2 pt-1.5 border-t border-base-200/50">
            <div className="space-y-1">
              <span className="text-base-content/70 font-semibold block text-[11px]">{t.highlightToggleLabel}</span>
              <button
                type="button"
                onClick={toggleHighlights}
                className={`btn btn-xs rounded-lg transition-colors w-full gap-1 ${
                  showHighlights 
                    ? 'btn-success bg-emerald-700 text-white border-0 hover:bg-emerald-800' 
                    : 'btn-outline btn-neutral opacity-60'
                }`}
              >
                {showHighlights ? (
                  <>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>{t.toggleOn}</span>
                  </>
                ) : (
                  <span>{t.toggleOff}</span>
                )}
              </button>
            </div>

            <div className="space-y-1">
              <span className="text-base-content/70 font-semibold block text-[11px]">{t.densityLabel}</span>
              <button
                type="button"
                onClick={toggleCompactView}
                className={`btn btn-xs rounded-lg transition-colors w-full ${
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
      )}
    </div>
  );
};
