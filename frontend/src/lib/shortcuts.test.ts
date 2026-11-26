import { describe, expect, it } from 'vitest';
import { GO_KEYS, interpretKey } from './shortcuts';

const none = { ctrl: false, meta: false, alt: false };

describe('interpretKey', () => {
  it('waits after g and then jumps to the page', () => {
    expect(interpretKey('g', false, none)).toEqual({ type: 'wait-g' });
    expect(interpretKey('d', true, none)).toEqual({ type: 'go', to: '/dcf' });
    expect(interpretKey('R', true, none)).toEqual({ type: 'go', to: '/ratios' });
  });
  it('ignores an unknown second key', () => {
    expect(interpretKey('z', true, none)).toBeNull();
  });
  it('opens help and search', () => {
    expect(interpretKey('?', false, none)).toEqual({ type: 'help' });
    expect(interpretKey('/', false, none)).toEqual({ type: 'search' });
  });
  it('leaves keys with modifiers to the browser', () => {
    expect(interpretKey('g', false, { ...none, ctrl: true })).toBeNull();
    expect(interpretKey('/', false, { ...none, meta: true })).toBeNull();
  });
  it('maps every shortcut to a distinct page', () => {
    const targets = Object.values(GO_KEYS).map((g) => g.to);
    expect(new Set(targets).size).toBe(targets.length);
  });
});
