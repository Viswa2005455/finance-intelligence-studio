import { describe, expect, it } from 'vitest';
import { attention, whenText, type CalItem } from './complianceCalendar';

const item = (id: string, days: number, status: CalItem['status']): CalItem => ({ id, date: '2026-11-21', area: 'income_tax', title: id, detail: '', days, status, source: null });

describe('compliance calendar helpers', () => {
  it('keeps only what needs attention and has not been filed', () => {
    const items = [item('a', -3, 'overdue'), item('b', 2, 'soon'), item('c', 40, 'later'), item('d', 0, 'today')];
    expect(attention(items, ['d']).map((i) => i.id)).toEqual(['a', 'b']);
  });
  it('words the distance in days', () => {
    expect(whenText({ days: 0 })).toBe('today');
    expect(whenText({ days: 1 })).toBe('tomorrow');
    expect(whenText({ days: 5 })).toBe('in 5 days');
    expect(whenText({ days: -1 })).toBe('yesterday');
    expect(whenText({ days: -4 })).toBe('4 days ago');
  });
});
