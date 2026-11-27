import { describe, expect, it } from 'vitest';
import { diffVersions } from './versionDiff';

describe('diffVersions', () => {
  it('finds edited, added and removed values by path', () => {
    const before = { wacc: 0.11, growth: [0.1, 0.09], debt: { bank: 300 }, old: 1 };
    const after = { wacc: 0.1, growth: [0.1, 0.09, 0.08], debt: { bank: 300 }, shares: 50 };
    const d = diffVersions(before, after);
    expect(d).toContainEqual({ path: 'wacc', before: '0.11', after: '0.1', kind: 'changed' });
    expect(d).toContainEqual({ path: 'growth[3]', before: null, after: '0.08', kind: 'added' });
    expect(d).toContainEqual({ path: 'shares', before: null, after: '50', kind: 'added' });
    expect(d).toContainEqual({ path: 'old', before: '1', after: null, kind: 'removed' });
    expect(d.some((c) => c.path === 'debt.bank')).toBe(false);
  });
  it('reports nothing when identical', () => {
    expect(diffVersions({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] })).toEqual([]);
  });
});
