import { chromium, expect, request, type FullConfig } from '@playwright/test';
import { existsSync, mkdirSync } from 'node:fs';

export const AUTH_FILE = 'e2e/.auth/user.json';
/** Every page of the signed-in app. */
export const ALL_PAGES = ['/', '/projects', '/upload', '/budgeting', '/forecasting', '/variance', '/costing', '/close', '/calendar', '/calculators', '/glossary', '/self-check', '/accounting', '/investments', '/markets', '/income-tax', '/gst',
  '/statements', '/ratios', '/cash-flow', '/red-flags', '/model-check', '/peers', '/scenarios', '/sensitivity', '/dcf', '/investment', '/code-lab', '/assistant',
  '/ai-health', '/reports', '/learn', '/settings'];
export const EMAIL = 'e2e-user@example.com';
export const PASSWORD = 'e2e-correct-horse-battery-9';

/**
 * Gets a signed-in session for the tests. The first run on a fresh database creates the account through the real
 * sign-up form (that is the sign-up test); later runs on a database that already has it sign in instead, because
 * sign-up is rate limited per address (10 an hour) and every test run should not use that allowance up.
 */
export default async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL ?? 'http://localhost:5173';
  mkdirSync('e2e/.auth', { recursive: true });
  if (existsSync(AUTH_FILE)) {  // a saved session that still works means no sign-in at all (sign-in is rate limited too)
    const api = await request.newContext({ baseURL, storageState: AUTH_FILE });
    const alive = (await api.get('/api/auth/me')).ok();
    await api.dispose();
    if (alive) return;
  }
  const browser = await chromium.launch({ channel: 'chrome' });
  const page = await browser.newPage({ baseURL });
  await page.goto('/');
  await page.getByRole('button', { name: 'Sign in' }).first().click();
  await page.getByLabel('Email').fill(EMAIL);
  await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).last().click();
  const welcome = page.getByRole('heading', { name: /Welcome back, E2E/ });
  const refused = page.getByText('Email or password is incorrect.');
  await expect(welcome.or(refused)).toBeVisible({ timeout: 30_000 });
  if (await refused.isVisible()) {
    await page.getByRole('button', { name: 'Create an account' }).click();
    await page.getByLabel('Your name').fill('E2E Tester');
    await page.getByLabel('Email').fill(EMAIL);
    await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
    await page.getByRole('button', { name: 'Create account' }).click();
    await expect(welcome).toBeVisible({ timeout: 30_000 });
  }
  await page.context().storageState({ path: AUTH_FILE });
  await browser.close();
}
