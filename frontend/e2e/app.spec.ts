import { expect, test } from '@playwright/test';
import { AUTH_FILE } from './global-setup';

test.use({ storageState: AUTH_FILE });

test('a new account sees the first-run checklist', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('region', { name: 'Get started' })).toBeVisible();
  await expect(page.getByText(/Get started: \d of 3 done/)).toBeVisible();
});

test('Ctrl+K jumps to a page and the page opens with a plain-English reading', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Welcome back/ })).toBeVisible();
  await page.keyboard.press('Control+k');
  await page.getByRole('combobox', { name: 'Search pages' }).fill('npv');
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/investment/);
  await expect(page.getByText('In plain English')).toBeVisible();
  await expect(page.getByText('adds value at your required return')).toBeVisible();
});

test('DCF explains itself and its chart can be saved as a picture', async ({ page }) => {
  await page.goto('/dcf');
  await expect(page.getByText('In plain English')).toBeVisible();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: /Download FCFF by year as a picture/ }).first().click();
  expect((await download).suggestedFilename()).toBe('fcff-by-year.png');
});

test('ratios open with an overall reading and each ratio explains itself', async ({ page }) => {
  await page.goto('/ratios');
  await expect(page.getByRole('heading', { name: 'Overall reading' })).toBeVisible();
  await expect(page.getByText('Typical range').first()).toBeVisible();
});

test('budgeting shows the results before the setup', async ({ page }) => {
  await page.goto('/budgeting');
  const results = await page.getByText('Budgeted revenue').boundingBox();
  const setup = await page.getByText('Budget setup').boundingBox();
  expect(results && setup && results.y < setup.y).toBe(true);
});

test('messy files are read, with decimal commas fixed and the sources shown', async ({ page }) => {
  await page.goto('/upload');
  await page.locator('input[type=file]').setInputFiles([
    { name: 'eu-report.csv', mimeType: 'text/csv', buffer: Buffer.from('Posten;2024;2025\nUmsatz;11000,50;12480,75\nGewinn;1150,25;1380,10\n') },
    { name: 'summary.txt', mimeType: 'text/plain', buffer: Buffer.from('Revenue in FY24 was 11,000 and in FY25 it was 12,480.\nNet profit in FY24 was 1,150 and in FY25 it was 1,380.\n') },
    { name: 'export.dat', mimeType: 'application/octet-stream', buffer: Buffer.from('Item,2024,2025\nRevenue,11000,12480\nCOGS,7260,8360\n') },
  ]);
  await expect(page.getByText('eu-report.csv').first()).toBeVisible();
  await expect(page.getByText('summary.txt').first()).toBeVisible();
  await expect(page.getByText('export.dat').first()).toBeVisible();

  await page.getByRole('button', { name: /eu-report\.csv/ }).first().click();
  await expect(page.getByText(/use a decimal comma/).first()).toBeVisible();
  await expect(page.getByText('11,000.50').first()).toBeVisible();

  await page.getByRole('button', { name: /summary\.txt/ }).first().click();
  await expect(page.getByText('Revenue').first()).toBeVisible();
  await expect(page.getByText('Revenue: change FY24 → FY25')).toBeVisible();  // numbers from sentences reach the calculation engines

  await page.getByRole('button', { name: /export\.dat/ }).first().click();
  await expect(page.getByText('Delimited data file').first()).toBeVisible();
});

test('a program is refused with a clear reason', async ({ page }) => {
  await page.goto('/upload');
  await page.locator('input[type=file]').setInputFiles({ name: 'run.exe', mimeType: 'application/octet-stream', buffer: Buffer.from('MZ') });
  await expect(page.getByText(/never accepted/)).toBeVisible();
});
