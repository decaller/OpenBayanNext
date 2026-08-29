import React from 'react';
import type { SupportedLanguage } from '../../lib/i18n';
import { setLanguage } from '../../stores/workspace';

interface LanguageSwitcherProps {
  currentLang: SupportedLanguage;
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ currentLang }) => {
  const languages: { code: SupportedLanguage; label: string; flag: string }[] = [
    { code: 'ar', label: 'العربية', flag: '🇸🇦' },
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'id', label: 'Indonesia', flag: '🇮🇩' },
  ];

  return (
    <div className="dropdown dropdown-end font-sans">
      <div 
        tabIndex={0} 
        role="button" 
        className="btn btn-ghost btn-xs sm:btn-sm gap-1.5 border border-base-200/80 bg-base-100/60"
        title="تغيير لغة الواجهة / Change Language"
      >
        <svg className="w-4 h-4 text-emerald-800 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
        <span className="font-semibold text-xs">
          {languages.find(l => l.code === currentLang)?.label || 'العربية'}
        </span>
      </div>
      <ul 
        tabIndex={0} 
        className="dropdown-content z-50 menu p-1 shadow-lg bg-base-100 rounded-box w-36 border border-base-200 text-xs mt-1"
      >
        {languages.map((l) => (
          <li key={l.code}>
            <button
              type="button"
              onClick={() => setLanguage(l.code)}
              className={`flex items-center justify-between py-2 ${currentLang === l.code ? 'active bg-emerald-800 text-white font-bold' : ''}`}
            >
              <span>{l.label}</span>
              <span>{l.flag}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
