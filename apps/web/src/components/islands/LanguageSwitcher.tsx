import React from 'react';
import type { SupportedLanguage } from '../../lib/i18n';
import { translations } from '../../lib/i18n';
import { setLanguage } from '../../stores/workspace';

interface LanguageSwitcherProps {
  currentLang: SupportedLanguage;
  compact?: boolean;
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ currentLang, compact = false }) => {
  const t = translations[currentLang];
  const languages: { code: SupportedLanguage; label: string; flag: string }[] = [
    { code: 'ar', label: 'العربية', flag: '🇸🇦' },
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'id', label: 'Indonesia', flag: '🇮🇩' },
  ];

  const activeLang = languages.find(l => l.code === currentLang) || languages[0];

  return (
    <div className="dropdown dropdown-end font-sans">
      <div 
        tabIndex={0} 
        role="button" 
        className={`btn btn-ghost ${compact ? 'btn-xs' : 'btn-xs sm:btn-sm'} gap-1.5 border border-base-300/80 bg-base-100/70 hover:bg-base-200/90 shadow-2xs transition-all rounded-xl`}
        title={t.languageLabel}
        aria-label={t.languageLabel}
      >
        <span className="text-sm">{activeLang.flag}</span>
        <span className="text-xs font-semibold text-base-content">
          {activeLang.label}
        </span>
        <svg className="w-3 h-3 opacity-60 text-base-content" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      <ul 
        tabIndex={0} 
        className="dropdown-content z-50 menu p-1.5 shadow-xl bg-base-100/95 backdrop-blur-md rounded-2xl w-40 border border-base-300 text-xs mt-1.5 space-y-0.5"
      >
        <li className="menu-title px-2 py-1 text-[11px] font-bold text-base-content/60">
          {t.languageLabel}
        </li>
        {languages.map((l) => {
          const isSelected = currentLang === l.code;
          return (
            <li key={l.code}>
              <button
                type="button"
                onClick={() => setLanguage(l.code)}
                className={`flex items-center justify-between py-2 px-2.5 rounded-xl transition-all ${
                  isSelected
                    ? 'active font-bold bg-primary text-primary-content shadow-xs'
                    : 'hover:bg-base-200 text-base-content'
                }`}
              >
                <span>{l.label}</span>
                <span className="text-sm">{l.flag}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
