// Starts the API for the browser tests on a throwaway SQLite database: applies the migrations, then serves on :8000.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const backend = resolve(import.meta.dirname, '..', '..', 'backend');
const dir = mkdtempSync(join(tmpdir(), 'fis-e2e-'));
const env = {
  ...process.env,
  DATABASE_URL: `sqlite:///${join(dir, 'e2e.db').replaceAll('\\', '/')}`,
  FIS_STORAGE_DIR: dir,
  FIS_ENV: 'development',
};

const migrate = spawnSync('uv', ['run', 'alembic', 'upgrade', 'head'], { cwd: backend, env, stdio: 'inherit', shell: process.platform === 'win32' });
if (migrate.status !== 0) process.exit(migrate.status ?? 1);

const server = spawn('uv', ['run', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: backend, env, stdio: 'inherit', shell: process.platform === 'win32' });
const stop = () => { server.kill(); try { rmSync(dir, { recursive: true, force: true }); } catch { /* a locked file on Windows is fine */ } };
process.on('SIGTERM', () => { stop(); process.exit(0); });
process.on('SIGINT', () => { stop(); process.exit(0); });
server.on('exit', (code) => process.exit(code ?? 0));
