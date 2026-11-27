import { describe, expect, it } from 'vitest';
import { glossify } from './glossary';

const terms = (t: string) => glossify(t).filter((p): p is { term: string; def: string } => typeof p !== 'string').map((p) => p.term);

describe('glossify', () => {
  it('marks known terms and keeps the rest of the text', () => {
    const parts = glossify('WACC is only 1.0% above terminal growth.');
    expect(parts[0]).toMatchObject({ term: 'WACC' });
    expect(parts.map((p) => (typeof p === 'string' ? p : p.term)).join('')).toBe('WACC is only 1.0% above terminal growth.');
  });
  it('marks the first use of each term only', () => {
    expect(terms('NPV and then NPV again, plus IRR')).toEqual(['NPV', 'IRR']);
  });
  it('finds phrases in any case and prefers the longest match', () => {
    expect(terms('The Cash Conversion Cycle is long, and the current ratio is fine')).toEqual(['Cash Conversion Cycle', 'current ratio']);
  });
  it('does not mark acronyms inside other words or in the wrong case', () => {
    expect(terms('The firm is wacky and the dsos are odd')).toEqual([]);
    expect(terms('Check the irr by hand')).toEqual([]);
  });
  it('returns the text unchanged when nothing matches', () => {
    expect(glossify('Nothing special here.')).toEqual(['Nothing special here.']);
  });
});
