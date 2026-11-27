import { describe, expect, it } from 'vitest';
import { edit, MAX_HISTORY, MERGE_MS, redo, start, undo } from './history';

describe('history', () => {
  it('steps back and forward through separate changes', () => {
    let h = start(0);
    h = edit(h, 1, 1000, true);
    h = edit(h, 2, 2000, true);
    expect(h.cur).toBe(2);
    h = undo(h); expect(h.cur).toBe(1);
    h = undo(h); expect(h.cur).toBe(0);
    expect(undo(h)).toBe(h); // nothing left to undo
    h = redo(h); expect(h.cur).toBe(1);
    h = redo(h); expect(h.cur).toBe(2);
    expect(redo(h)).toBe(h);
  });

  it('merges quick typing into one step, but not slow edits', () => {
    let h = start(0);
    h = edit(h, 1, 1000);
    h = edit(h, 2, 1000 + MERGE_MS / 2);
    h = edit(h, 3, 1000 + MERGE_MS);
    expect(h.past).toEqual([0]); // one step covers 0 -> 3
    h = edit(h, 4, 1000 + MERGE_MS * 4);
    expect(h.past).toEqual([0, 3]);
    expect(undo(h).cur).toBe(3);
  });

  it('a new edit clears what was undone', () => {
    let h = start('a');
    h = edit(h, 'b', 1000, true);
    h = undo(h);
    expect(h.future).toEqual(['b']);
    h = edit(h, 'c', 5000);
    expect(h.future).toEqual([]);
  });

  it('keeps only the most recent steps', () => {
    let h = start(0);
    for (let i = 1; i <= MAX_HISTORY + 20; i++) h = edit(h, i, i * 10_000, true);
    expect(h.past.length).toBe(MAX_HISTORY);
    expect(h.past[0]).toBe(20);
  });
});
