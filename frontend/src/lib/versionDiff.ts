/** What changed between two saved versions of a model: every value that was added, removed or edited, by its path. */
export interface Change { path: string; before: string | null; after: string | null; kind: 'added' | 'removed' | 'changed' }

function flatten(v: unknown, path: string, out: Map<string, string>): void {
  if (v !== null && typeof v === 'object') {
    const entries = Array.isArray(v) ? v.map((x, i) => [String(i + 1), x] as const) : Object.entries(v as Record<string, unknown>);
    if (!entries.length) { out.set(path, Array.isArray(v) ? '[]' : '{}'); return; }
    for (const [k, x] of entries) flatten(x, path ? (Array.isArray(v) ? `${path}[${k}]` : `${path}.${k}`) : k, out);
  } else out.set(path, v === null || v === undefined ? 'empty' : String(v));
}

export function diffVersions(before: unknown, after: unknown): Change[] {
  const a = new Map<string, string>(), b = new Map<string, string>();
  flatten(before, '', a);
  flatten(after, '', b);
  const out: Change[] = [];
  for (const [path, x] of b) {
    if (!a.has(path)) out.push({ path, before: null, after: x, kind: 'added' });
    else if (a.get(path) !== x) out.push({ path, before: a.get(path)!, after: x, kind: 'changed' });
  }
  for (const [path, x] of a) if (!b.has(path)) out.push({ path, before: x, after: null, kind: 'removed' });
  return out;
}
