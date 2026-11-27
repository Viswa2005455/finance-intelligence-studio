import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { setNumberStyle, type Currency, type NumberStyle, type UnitScale } from './format';
import { load, save } from './storage';

export type ThemePref = 'system' | 'dark' | 'light';
export interface Settings {
  theme: ThemePref;
  currency: Currency;
  units: UnitScale;
  reduceMotion: boolean;
  /** The 3D background: moving, a still picture, or a plain canvas. */
  backdrop: 'scene' | 'off';
  /** Settings layout version: lets a new default background reach people who never chose one. */
  bgv: number;
  learningMode: boolean;
  periodFrom: string;
  periodTo: string;
  numberStyle: NumberStyle;
  /** Page text size: the whole interface is scaled. */
  textSize: 'normal' | 'large' | 'larger';
  /** Stronger text and borders, and no moving background. */
  contrast: 'normal' | 'high';
}

const DEFAULTS: Settings = {
  theme: 'system', currency: 'INR', units: 'lakhs', reduceMotion: false, backdrop: 'scene', bgv: 4, learningMode: true,
  periodFrom: '2025-11', periodTo: '2026-10', numberStyle: 'auto', textSize: 'normal', contrast: 'normal',
};

interface Ctx { settings: Settings; update: (p: Partial<Settings>) => void; resolvedTheme: 'dark' | 'light' }
const SettingsContext = createContext<Ctx | null>(null);

function systemDark() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(() => {
    const stored = load<Settings>('fis.settings', DEFAULTS);
    // Version 4 brings the 3D scene back, with the navy dark theme as the starting look. Everyone moves to it once; after that their choices are kept.
    const s: Settings = { ...DEFAULTS, ...stored, ...((stored.bgv ?? 1) < 4 ? { backdrop: 'scene' as const, theme: 'dark' as const, bgv: 4 } : {}) };
    setNumberStyle(s.numberStyle);
    return s;
  });
  const [sysDark, setSysDark] = useState(systemDark);

  useEffect(() => {
    const mq = window.matchMedia?.('(prefers-color-scheme: dark)');
    const on = () => setSysDark(mq.matches);
    mq?.addEventListener('change', on);
    return () => mq?.removeEventListener('change', on);
  }, []);

  const resolvedTheme = settings.theme === 'system' ? (sysDark ? 'dark' : 'light') : settings.theme;

  useEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme;
    document.documentElement.dataset.motion = settings.reduceMotion ? 'reduce' : 'auto';
    document.documentElement.dataset.backdrop = settings.backdrop;
    document.documentElement.dataset.textsize = settings.textSize;
    document.documentElement.dataset.contrast = settings.contrast;
  }, [resolvedTheme, settings.reduceMotion, settings.backdrop, settings.textSize, settings.contrast]);

  const update = useCallback((p: Partial<Settings>) => {
    setSettings((s) => {
      const next = { ...s, ...p };
      setNumberStyle(next.numberStyle);
      save('fis.settings', next);
      return next;
    });
  }, []);

  const value = useMemo(() => ({ settings, update, resolvedTheme }), [settings, update, resolvedTheme]);
  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const c = useContext(SettingsContext);
  if (!c) throw new Error('useSettings outside provider');
  return c;
}
