import React from 'react';
import { useStore } from '@nanostores/react';
import { $currentTheme, setTheme, type ThemeOption } from '../../stores/workspace';
import type { SupportedLanguage } from '../../lib/i18n';
import { translations } from '../../lib/i18n';

interface ThemeSwitcherProps {
  currentLang?: SupportedLanguage;
  compact?: boolean;
}

export const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ currentLang = 'ar', compact = false }) => {
  const currentTheme = useStore($currentTheme);
  const t = translations[currentLang];

  const themes: { id: ThemeOption; label: string; icon: string; bg: string; color: string }[] = [
    { id: 'auto', label: t.themeAuto, icon: '💻', bg: 'bg-gradient-to-r from-base-300 to-base-100', color: 'text-base-content' },
    { id: 'emerald', label: t.themeEmerald, icon: '🌿', bg: 'bg-[#66cc8a]', color: 'text-emerald-950' },
    { id: 'dim', label: t.themeDim, icon: '🌙', bg: 'bg-[#2a303c]', color: 'text-slate-200' },
    { id: 'cupcake', label: t.themeCupcake, icon: '📖', bg: 'bg-[#faf7f5]', color: 'text-amber-950' },
    { id: 'night', label: t.themeNight, icon: '🌌', bg: 'bg-[#0f172a]', color: 'text-sky-300' },
    { id: 'sunset', label: t.themeSunset, icon: '🌅', bg: 'bg-[#ff865b]', color: 'text-orange-950' },
  ];

  const activeThemeItem = themes.find(th => th.id === currentTheme) || themes[0];

  return (
    <div className="dropdown dropdown-end font-sans">
      <div
        tabIndex={0}
        role="button"
        className={`btn btn-ghost ${compact ? 'btn-xs' : 'btn-xs sm:btn-sm'} gap-1.5 border border-base-300/80 bg-base-100/70 hover:bg-base-200/90 shadow-2xs transition-all rounded-xl`}
        title={t.themeLabel}
        aria-label={t.themeLabel}
      >
        <span className="text-sm">{activeThemeItem.icon}</span>
        <span className="text-xs font-semibold hidden sm:inline text-base-content">
          {activeThemeItem.label.split(' ')[0]}
        </span>
        <svg className="w-3 h-3 opacity-60 text-base-content" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      <ul
        tabIndex={0}
        className="dropdown-content z-50 menu p-1.5 shadow-xl bg-base-100/95 backdrop-blur-md rounded-2xl w-48 sm:w-56 border border-base-300 text-xs mt-1.5 space-y-0.5"
      >
        <li className="menu-title px-2 py-1 text-[11px] font-bold text-base-content/60 flex items-center justify-between">
          <span>{t.themeLabel}</span>
          <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-base-200 text-base-content/70">
            {currentTheme}
          </span>
        </li>
        {themes.map((th) => {
          const isSelected = currentTheme === th.id;
          return (
            <li key={th.id}>
              <button
                type="button"
                onClick={() => setTheme(th.id)}
                className={`flex items-center justify-between py-2 px-2.5 rounded-xl transition-all ${
                  isSelected
                    ? 'active font-bold bg-primary text-primary-content shadow-xs'
                    : 'hover:bg-base-200 text-base-content'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm">{th.icon}</span>
                  <span className="truncate">{th.label}</span>
                </div>
                <div
                  className={`w-3.5 h-3.5 rounded-full border border-base-300 shadow-2xs flex-shrink-0 ${th.bg}`}
                />
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
