import { describe, expect, it } from 'vitest';
import { currentMonth, freshChecklist, nextMonth, progress, TEMPLATE } from './closeChecklist';

describe('close checklist', () => {
  it('starts with every step open', () => {
    const s = freshChecklist('2026-11');
    expect(s.items).toHaveLength(TEMPLATE.length);
    expect(progress(s)).toEqual({ done: 0, total: TEMPLATE.length, pct: 0 });
  });
  it('counts finished steps', () => {
    const s = freshChecklist('2026-11');
    s.items[0].done = true;
    s.items[1].done = true;
    const p = progress(s);
    expect(p.done).toBe(2);
    expect(p.pct).toBe(Math.round((2 / TEMPLATE.length) * 100));
  });
  it('rolls to the next month, keeping owners and clearing ticks and notes', () => {
    const s = freshChecklist('2026-11');
    s.items[0] = { ...s.items[0], done: true, owner: 'Asha', note: 'Axis matched' };
    const n = nextMonth(s);
    expect(n.month).toBe('2026-12');
    expect(n.items[0]).toMatchObject({ done: false, owner: 'Asha', note: '' });
  });
  it('rolls December into January of the next year', () => {
    expect(nextMonth(freshChecklist('2026-12')).month).toBe('2027-01');
  });
  it('formats the current month', () => {
    expect(currentMonth(new Date(2026, 0, 15))).toBe('2026-01');
  });
  it('links only to pages that exist', () => {
    const pages = new Set(['/upload', '/cash-flow', '/ratios', '/accounting', '/income-tax', '/gst', '/statements', '/variance', '/red-flags']);
    for (const i of TEMPLATE) if (i.to) expect(pages.has(i.to)).toBe(true);
  });
});
