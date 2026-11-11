import { useCallback, useEffect, useState } from 'react';
import { loadRaw, save } from './storage';

const KEY = 'fis.guide';
const EVENT = 'fis-guide-changed';

interface GuideState { dismissed: string[]; off: boolean }
const read = (): GuideState => {
  const s = loadRaw<Partial<GuideState>>(KEY, {});
  return { dismissed: Array.isArray(s.dismissed) ? s.dismissed : [], off: !!s.off };
};

/**
 * First-time help ("tips"): which tips the user has dismissed, and whether they switched tips off altogether.
 * Kept in this browser only. Every component using it stays in step through a small window event.
 */
export function useGuide() {
  const [state, setState] = useState<GuideState>(read);
  useEffect(() => {
    const sync = () => setState(read());
    window.addEventListener(EVENT, sync);
    window.addEventListener('storage', sync);
    return () => { window.removeEventListener(EVENT, sync); window.removeEventListener('storage', sync); };
  }, []);
  const write = useCallback((next: GuideState) => { save(KEY, next); setState(next); window.dispatchEvent(new Event(EVENT)); }, []);
  const isOn = useCallback((id: string) => !state.off && !state.dismissed.includes(id), [state]);
  const dismiss = useCallback((id: string) => { const s = read(); if (!s.dismissed.includes(id)) write({ ...s, dismissed: [...s.dismissed, id] }); }, [write]);
  const setOff = useCallback((off: boolean) => write({ ...read(), off }), [write]);
  const reset = useCallback(() => write({ dismissed: [], off: false }), [write]);
  return { isOn, dismiss, setOff, reset, off: state.off };
}
