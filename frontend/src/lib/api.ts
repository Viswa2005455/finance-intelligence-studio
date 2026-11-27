/** Thin fetch wrapper. All requests go to the FastAPI backend under /api (proxied by Vite in dev). */

export class ApiError extends Error {
  status: number;
  /** Machine-readable reason from the server (e.g. AI error categories such as "timeout" or "rate_limit"). */
  category?: string;
  constructor(message: string, status: number, category?: string) {
    super(message);
    this.status = status;
    this.category = category;
  }
}

/** Options for one request: a caller's AbortSignal cancels it (e.g. when newer inputs arrive). */
export interface RequestOpts { signal?: AbortSignal; timeoutMs?: number }

export const isAbort = (e: unknown) => e instanceof DOMException && e.name === 'AbortError';

/** Fired when the server says the session is missing or expired; the auth provider listens for it. */
export const UNAUTHORIZED_EVENT = 'fis:unauthorized';
function signalUnauthorized(path: string) {
  if (!path.startsWith('/api/auth/')) window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
}

const BACKEND_DOWN = 'The calculation server is not answering yet. It may still be starting: wait about 20 seconds and press Retry. If you run the app on your own PC, check that the "Finance Studio - BACKEND" window is open (run start-windows.bat again if it is closed).';
const SERVER_FAULT = 'Something went wrong on our side while handling this request. Your data and your other work are safe. Try again in a moment; if it keeps happening, copy the details below and send them to support.';
const DEFAULT_TIMEOUT_MS = 60_000;

/** Technical details for each friendly message, so the error box can offer "Copy details" without
 * showing jargon to everyone. Keyed by the message text the user sees. */
export const problemLog = new Map<string, string>();
function remember(message: string, method: string, path: string, status: number, raw?: string): void {
  const lines = [`Time: ${new Date().toISOString()}`, `Request: ${method} ${path}`, `Status: ${status || 'no response'}`];
  if (raw && raw !== message) lines.push(`Server said: ${raw}`);
  if (problemLog.size > 50) problemLog.delete(problemLog.keys().next().value as string);
  problemLog.set(message, lines.join('\n'));
}

/** FastAPI validation errors arrive as a list of {loc, msg}; turn them into one readable sentence. */
function validationText(detail: unknown): string | null {
  if (!Array.isArray(detail) || !detail.length) return null;
  const parts = detail.slice(0, 3).map((d) => {
    const loc = Array.isArray(d?.loc) ? d.loc.filter((x: unknown) => x !== 'body').join(' › ') : '';
    const msg = typeof d?.msg === 'string' ? d.msg.replace(/^Value error, /, '') : 'is not valid';
    return loc ? `${loc}: ${msg}` : msg;
  });
  return `Some inputs need attention. ${parts.join('; ')}${detail.length > 3 ? `; and ${detail.length - 3} more` : ''}.`;
}

function friendlyStatus(status: number, detail: unknown, hasBody: boolean): { message: string; category?: string } {
  if (typeof detail === 'string' && detail && !/^internal error/i.test(detail)) return { message: detail };
  const v = validationText(detail);
  if (v) return { message: v, category: 'validation' };
  if (!hasBody && [500, 502, 503, 504].includes(status)) return { message: BACKEND_DOWN, category: 'network' };
  if (status >= 500) return { message: SERVER_FAULT, category: 'server' };
  if (status === 404) return { message: 'We could not find what you asked for. It may have been deleted or moved.', category: 'not_found' };
  if (status === 413) return { message: 'That file or request is too large. Try a smaller file or split it into parts.', category: 'too_large' };
  if (status === 429) return { message: 'Too many requests in a short time. Wait a minute and try again.', category: 'rate_limit' };
  if (status === 403) return { message: 'You do not have permission to do that.', category: 'forbidden' };
  return { message: `This request could not be completed (code ${status}). Check your inputs and try again.` };
}

async function once<T>(path: string, init: RequestInit, opts: RequestOpts): Promise<T> {
  const ctl = new AbortController();
  const timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  let timedOut = false;
  const timer = setTimeout(() => { timedOut = true; ctl.abort(); }, timeoutMs);
  const forward = () => ctl.abort();
  if (opts.signal?.aborted) ctl.abort();
  opts.signal?.addEventListener('abort', forward);
  try {
    let res: Response;
    let text: string;
    try {
      res = await fetch(path, { ...init, signal: ctl.signal });
      text = await res.text();
    } catch (e) {
      if (opts.signal?.aborted) throw new DOMException('Request cancelled', 'AbortError');
      if (timedOut) throw new ApiError(`The server did not answer within ${Math.round(timeoutMs / 1000)} seconds. Try again.`, 0, 'timeout');
      remember(BACKEND_DOWN, init.method ?? 'GET', path, 0);
      throw new ApiError(BACKEND_DOWN, 0, isAbort(e) ? 'aborted' : 'network');
    }
    let body: unknown = null;
    try {
      body = text ? JSON.parse(text) : null;
    } catch {
      // non-JSON (e.g. proxy error page)
    }
    if (res.status === 401) signalUnauthorized(path);
    if (!res.ok) {
      const detail = (body as { detail?: unknown } | null)?.detail;
      if (detail && typeof detail === 'object' && 'message' in detail) {
        const d = detail as { message: string; category?: string };
        throw new ApiError(d.message, res.status, d.category);
      }
      const f = friendlyStatus(res.status, detail, body !== null);
      remember(f.message, init.method ?? 'GET', path, res.status, typeof detail === 'string' ? detail : undefined);
      throw new ApiError(f.message, res.status, f.category);
    }
    return body as T;
  } finally {
    clearTimeout(timer);
    opts.signal?.removeEventListener('abort', forward);
  }
}

async function request<T>(path: string, init: RequestInit = {}, opts: RequestOpts = {}): Promise<T> {
  const idempotent = !init.method || init.method === 'GET';
  try {
    return await once<T>(path, init, opts);
  } catch (e) {
    // One retry for reads that failed on the network or a gateway hiccup; writes are never repeated.
    const retryable = e instanceof ApiError && (e.category === 'network' || e.status === 502 || e.status === 503);
    if (!idempotent || !retryable || opts.signal?.aborted) throw e;
    await new Promise((r) => setTimeout(r, 1200));
    return once<T>(path, init, opts);
  }
}

export const api = {
  get: <T>(path: string, opts?: RequestOpts) => request<T>(path, {}, opts),
  post: <T>(path: string, data: unknown, opts?: RequestOpts) =>
    request<T>(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }, opts),
  del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  put: <T>(path: string, data: unknown) =>
    request<T>(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),
  patch: <T>(path: string, data: unknown) =>
    request<T>(path, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),
  /** POST multipart form fields and files (each field name maps to a string or a File). */
  form: <T>(path: string, fields: Record<string, string | File | null | undefined>) => {
    const fd = new FormData();
    Object.entries(fields).forEach(([k, v]) => { if (v instanceof File) fd.append(k, v, v.name); else if (v != null && v !== '') fd.append(k, v); });
    return request<T>(path, { method: 'POST', body: fd });
  },
  upload: <T>(path: string, files: File[]) => {
    const fd = new FormData();
    files.forEach((f) => fd.append('files', f, f.name));
    return request<T>(path, { method: 'POST', body: fd });
  },
};

/** POST JSON and save the returned file (Excel, Word, …) under the server's suggested name. */
export const downloadPost = (path: string, data: unknown, fallbackName: string): Promise<void> => saveResponse('POST', path, data, fallbackName);
/** GET a file (for example the Excel workbook of saved models) and save it under the server's suggested name. */
export const downloadGet = (path: string, fallbackName: string): Promise<void> => saveResponse('GET', path, undefined, fallbackName);

async function saveResponse(method: 'GET' | 'POST', path: string, data: unknown, fallbackName: string): Promise<void> {
  let res: Response;
  try {
    res = await fetch(path, method === 'GET' ? { method } : { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  } catch {
    throw new ApiError(BACKEND_DOWN, 0);
  }
  if (res.status === 401) signalUnauthorized(path);
  if (!res.ok) {
    let detail: unknown;
    let hasBody = false;
    try { const b = await res.json(); hasBody = true; detail = typeof b?.detail?.message === 'string' ? b.detail.message : b?.detail; } catch { /* not JSON */ }
    const f = friendlyStatus(res.status, detail, hasBody);
    remember(f.message, method, path, res.status, typeof detail === 'string' ? detail : undefined);
    throw new ApiError(f.message, res.status, f.category);
  }
  const name = /filename="([^"]+)"/.exec(res.headers.get('content-disposition') ?? '')?.[1] ?? fallbackName;
  const url = URL.createObjectURL(await res.blob());
  const a = Object.assign(document.createElement('a'), { href: url, download: name });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Multipart upload with real byte-level progress (fetch cannot report upload progress). */
export function uploadWithProgress<T>(path: string, files: File[], onProgress: (fraction: number) => void, fields: Record<string, string | null | undefined> = {}): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const fd = new FormData();
    files.forEach((f) => fd.append('files', f, f.name));
    Object.entries(fields).forEach(([k, v]) => { if (v) fd.append(k, v); });
    xhr.open('POST', path);
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) onProgress(e.loaded / e.total); };
    xhr.onerror = () => reject(new ApiError('Upload failed: cannot reach the backend.', 0));
    xhr.onload = () => {
      let body: { detail?: unknown } | null = null;
      try { body = JSON.parse(xhr.responseText); } catch { /* ignore */ }
      if (xhr.status === 401) signalUnauthorized(path);
      if (xhr.status >= 200 && xhr.status < 300) resolve(body as T);
      else {
        const f = friendlyStatus(xhr.status, body?.detail, body !== null);
        remember(f.message, 'POST', path, xhr.status, typeof body?.detail === 'string' ? body.detail : undefined);
        reject(new ApiError(f.message, xhr.status, f.category));
      }
    };
    xhr.send(fd);
  });
}
