import { useEffect, useState } from 'react';
import { api } from './api';
import { loadRaw } from './storage';
import type { UploadSummary } from './types';

/** Statement data as saved by the Financial Statements page. */
export interface StatementData {
  periods: string[]; lines: { label: string; statement: string; key: string | null; values: (number | null)[]; source?: string | null }[];
  company?: string; units?: string; currency?: string; market?: Record<string, (number | null)[]>;
}
export interface CompanyData { periods: string[]; items: Record<string, (number | null)[]> }
export interface CompanySource { id: string; name: string; isExample: boolean; load: () => Promise<StatementData> }

/** Statement-shaped sheets the upload parser found (labels in a column, one column per period). */
export interface SuggestedSheet {
  sheet: string; statement: string; periods: string[]; months?: number | null;
  lines: { label: string; key: string | null; values: (number | null)[]; source: string | null }[];
}

/** Lines mapped to a standard item become engine inputs; unmapped lines are ignored. */
export function toCompany(d: StatementData): CompanyData {
  const items: Record<string, (number | null)[]> = {};
  const clean = (vs: (number | null)[]) => vs.map((v) => (typeof v === 'number' && Number.isFinite(v) ? v : null));
  for (const l of d.lines) if (l.key) items[l.key] = clean(l.values);
  for (const [k, vs] of Object.entries(d.market ?? {})) if (vs.length === d.periods.length) items[k] = clean(vs);
  return { periods: d.periods, items };
}

/**
 * One company from an upload's statement sheets, built the way the Financial Statements page imports them:
 * when a statement appears with several reporting lengths (for example 3-month and 12-month columns) the
 * longest is used, and each standard item is taken from the first line that matches it.
 */
export function statedUnits(ctx?: { currencies?: Record<string, number>; units?: Record<string, number> } | null): { currency?: string; units?: string } {
  const top = (o?: Record<string, number>) => Object.entries(o ?? {}).sort((a, b) => b[1] - a[1])[0]?.[0];
  return { currency: top(ctx?.currencies), units: top(ctx?.units) };
}

export function statementDataFromUpload(name: string, sheets: SuggestedSheet[], ctx?: { currencies?: Record<string, number>; units?: Record<string, number> } | null): StatementData | null {
  if (!sheets?.length) return null;
  const longest = new Map<string, number>();
  sheets.forEach((s) => longest.set(s.statement, Math.max(longest.get(s.statement) ?? 0, s.months ?? 0)));
  const chosen = sheets.filter((s) => (s.months ?? 0) === longest.get(s.statement));
  const periods: string[] = [];
  chosen.forEach((s) => s.periods.forEach((p) => { if (!periods.includes(p)) periods.push(p); }));
  const used = new Set<string>();
  const lines = chosen.flatMap((s) => s.lines.map((l) => {
    const key = l.key && !used.has(l.key) ? l.key : null;
    if (key) used.add(key);
    return { label: l.label, statement: s.statement, key, source: l.source,
      values: periods.map((p) => { const i = s.periods.indexOf(p); return i >= 0 ? l.values[i] : null; }) };
  }));
  return { periods, lines, company: name.replace(/\.[A-Za-z0-9]+$/, ''), ...statedUnits(ctx) };
}

/**
 * The data currently open on the Financial Statements page, every saved statements model, and every uploaded
 * file that holds statements, so a file just uploaded can be analysed without saving it as a company first.
 */
export function useCompanySources() {
  const [sources, setSources] = useState<CompanySource[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const current = loadRaw<{ data: StatementData; isExample: boolean } | null>('fis.statements', null);
    const list: CompanySource[] = [];
    const addCurrent = () => {
      if (!current?.data?.periods?.length) return;
      const name = current.isExample ? 'Financial Statements page (example data)'
        : current.data.company ? `${current.data.company} (open on Financial Statements, unsaved)` : 'Financial Statements page (unsaved)';
      list.push({ id: 'current', name, isExample: !!current.isExample, load: async () => current.data });
    };
    const addUploads = async () => {
      try {
        const r = await api.get<{ uploads: UploadSummary[] }>('/api/uploads');
        for (const u of r.uploads) {
          if (u.status !== 'processed' || !u.recommendations.some((x) => x.module === 'Financial Statements')) continue;
          list.push({ id: `upload:${u.id}`, name: `${u.name} (uploaded file)`, isExample: false, load: async () => {
            const rec = await api.get<{ name: string; statements: SuggestedSheet[] | null; analysis?: { context?: { currencies?: Record<string, number>; units?: Record<string, number> } } }>(`/api/uploads/${u.id}`);
            const d = statementDataFromUpload(rec.name, rec.statements ?? [], rec.analysis?.context);
            if (!d) throw new Error('No statement-shaped sheets were found in that file.');
            return d;
          } });
        }
      } catch { /* uploads are optional here */ }
    };
    api.get<{ items: { id: string; name: string }[] }>('/api/saved?kind=statements')
      .then(async (r) => {
        for (const it of r.items) list.push({ id: it.id, name: it.name, isExample: false,
          load: async () => (await api.get<{ data: StatementData }>(`/api/saved/${it.id}`)).data });
        addCurrent();
        await addUploads();
        setSources([...list]);
      })
      .catch(async (e) => { setError((e as Error).message); addCurrent(); await addUploads(); setSources([...list]); });
  }, []);
  return { sources, error };
}
