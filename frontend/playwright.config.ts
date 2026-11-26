import { defineConfig, devices } from '@playwright/test';

/**
 * Browser tests: sign-up, upload of messy files, key calculators, the command palette, mobile layout and accessibility.
 * They drive the real website and the real API (a throwaway SQLite database), and use the installed Google Chrome
 * so no browser needs downloading. Locally they reuse servers that are already running on ports 5173 and 8000.
 */
export default defineConfig({
  testDir: './e2e',
  globalSetup: './e2e/global-setup.ts',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: { baseURL: 'http://localhost:5173', channel: 'chrome', trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], channel: 'chrome', viewport: { width: 1280, height: 800 } }, testIgnore: /mobile\.spec\.ts/ },
    { name: 'phone', use: { ...devices['Pixel 7'], channel: 'chrome' }, testMatch: /mobile\.spec\.ts/ },
  ],
  webServer: [
    { command: 'node e2e/start-backend.mjs', url: 'http://127.0.0.1:8000/api/health', reuseExistingServer: !process.env.CI, timeout: 180_000 },
    { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: !process.env.CI, timeout: 120_000 },
  ],
});
