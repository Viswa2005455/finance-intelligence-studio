// Fails the build when the website grows past its size budget (gzip sizes, what a visitor actually downloads).
// Run after `npm run build`. Raise a limit on purpose, in this file, when a feature really needs it.
import { readdirSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { gzipSync } from 'node:zlib';

const dir = resolve(import.meta.dirname, '..', 'dist', 'assets');
const KB = 1024;
const budget = {
  entry: { match: /^index-.*\.js$/, max: 150 * KB, label: 'main entry script' },
  charts: { match: /^charts-.*\.js$/, max: 130 * KB, label: 'charts library chunk' },
  page: { match: /\.js$/, max: 60 * KB, label: 'any other page chunk' },
  css: { match: /\.css$/, max: 60 * KB, label: 'stylesheet' },
};
const TOTAL_MAX = 650 * KB;

let files;
try { files = readdirSync(dir); } catch { console.error('dist/assets not found: run `npm run build` first.'); process.exit(2); }

let failed = false;
let total = 0;
for (const f of files.filter((n) => /\.(js|css)$/.test(n))) {
  const size = gzipSync(readFileSync(join(dir, f))).length;
  if (f.endsWith('.js')) total += size;
  const rule = [budget.entry, budget.charts, budget.css, budget.page].find((b) => b.match.test(f));
  if (rule && size > rule.max) {
    failed = true;
    console.error(`OVER BUDGET  ${f}: ${(size / KB).toFixed(1)} KB gzip, limit ${(rule.max / KB).toFixed(0)} KB (${rule.label})`);
  }
}
if (total > TOTAL_MAX) { failed = true; console.error(`OVER BUDGET  all scripts together: ${(total / KB).toFixed(0)} KB gzip, limit ${(TOTAL_MAX / KB).toFixed(0)} KB`); }
console.log(`Bundle check ${failed ? 'FAILED' : 'passed'}: ${(total / KB).toFixed(0)} KB of scripts (gzip) across ${files.filter((n) => n.endsWith('.js')).length} files.`);
process.exit(failed ? 1 : 0);
