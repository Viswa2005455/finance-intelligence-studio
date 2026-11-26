import { Copy, ImageDown } from 'lucide-react';
import { downloadFile } from '../lib/format';
import { useToast } from '../lib/toast';

const PAINT = ['fill', 'stroke', 'stop-color', 'color'] as const;

/** Copy resolved colours and fonts onto a cloned chart so it still looks right outside the page
 * (a standalone SVG cannot see CSS variables such as var(--chart-1)). */
function inlineStyles(orig: Element, clone: Element): void {
  const cs = getComputedStyle(orig);
  const el = clone as SVGElement;
  for (const p of PAINT) {
    const attr = el.getAttribute(p);
    if (attr && attr.includes('var(')) el.setAttribute(p, cs.getPropertyValue(p));
  }
  if (el.tagName.toLowerCase() === 'text') {
    el.setAttribute('font-family', cs.fontFamily);
    if (!el.getAttribute('font-size')) el.setAttribute('font-size', cs.fontSize);
  }
  const style = el.getAttribute('style');
  if (style?.includes('var(')) el.setAttribute('style', style.replace(/var\((--[\w-]+)\)/g, (_, v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim()));
  const o = Array.from(orig.children);
  const c = Array.from(clone.children);
  o.forEach((child, i) => c[i] && inlineStyles(child, c[i]));
}

/** Render the chart's SVG to a PNG and download it. */
export async function chartToPng(svg: SVGSVGElement, name: string): Promise<void> {
  const box = svg.getBoundingClientRect();
  const w = Math.max(1, Math.round(box.width));
  const h = Math.max(1, Math.round(box.height));
  const clone = svg.cloneNode(true) as SVGSVGElement;
  inlineStyles(svg, clone);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clone.setAttribute('width', String(w));
  clone.setAttribute('height', String(h));
  const xml = new XMLSerializer().serializeToString(clone);
  const img = new Image();
  const url = URL.createObjectURL(new Blob([xml], { type: 'image/svg+xml;charset=utf-8' }));
  try {
    await new Promise<void>((res, rej) => { img.onload = () => res(); img.onerror = () => rej(new Error('The chart could not be drawn.')); img.src = url; });
    const scale = 2;
    const canvas = Object.assign(document.createElement('canvas'), { width: w * scale, height: h * scale });
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('This browser cannot draw the picture.');
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--bg-elev').trim() || '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    const blob: Blob | null = await new Promise((res) => canvas.toBlob(res, 'image/png'));
    if (!blob) throw new Error('The picture could not be saved.');
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `${name}.png` });
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  } finally {
    URL.revokeObjectURL(url);
  }
}

/** Tab-separated text of the chart's data: pastes straight into Excel or Sheets. */
export function rowsToTsv(rows: Record<string, unknown>[]): string {
  if (!rows.length) return '';
  const keys = Object.keys(rows[0]);
  const cell = (v: unknown) => (v === null || v === undefined ? '' : String(Array.isArray(v) ? v.join(' to ') : v)).replace(/[\t\r\n]+/g, ' ');
  return [keys.join('\t'), ...rows.map((r) => keys.map((k) => cell(r[k])).join('\t'))].join('\n');
}

/** Small "save as picture" and "copy the data" buttons for the chart in the card they sit in.
 * Put it in a Card's `actions`. `rows` is the chart's data (optional): it enables Copy data and CSV. */
export function ChartActions({ name, rows }: { name: string; rows?: Record<string, unknown>[] }) {
  const toast = useToast();
  const svgOf = (el: HTMLElement) => el.closest('section')?.querySelector('svg.recharts-surface') as SVGSVGElement | null;
  return (
    <>
      <button className="btn icon sm ghost" aria-label={`Download ${name} as a picture`} title="Download as picture (PNG)"
        onClick={async (e) => {
          const svg = svgOf(e.currentTarget);
          if (!svg) { toast('There is no chart to save yet.', 'error'); return; }
          try { await chartToPng(svg, name.toLowerCase().replace(/[^a-z0-9]+/g, '-')); } catch (err) { toast((err as Error).message, 'error'); }
        }}><ImageDown size={15} /></button>
      {rows && rows.length > 0 && (
        <button className="btn icon sm ghost" aria-label={`Copy the data behind ${name}`} title="Copy the data (paste into Excel)"
          onClick={async () => {
            try { await navigator.clipboard.writeText(rowsToTsv(rows)); toast('Chart data copied. Paste it into Excel or Sheets.'); }
            catch { downloadFile(`${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.csv`, rowsToTsv(rows).replace(/\t/g, ',')); toast('Clipboard blocked, so the data was downloaded instead.'); }
          }}><Copy size={15} /></button>
      )}
    </>
  );
}
