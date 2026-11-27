import { expect, test } from '@playwright/test';
import { AUTH_FILE } from './global-setup';

test.use({ storageState: AUTH_FILE });

// The tests share one account, and uploaded files and saved companies change what the Overview shows. Start every test from a clean account.
test.beforeEach(async ({ request }) => {
  const list = await (await request.get('/api/uploads')).json();
  for (const u of list.uploads ?? []) await request.delete(`/api/uploads/${u.id}`);
  const saved = await (await request.get('/api/saved')).json();
  for (const i of saved.items ?? []) await request.delete(`/api/saved/${i.id}`);
});

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

test('keyboard shortcuts: g then d opens the DCF, ? shows the list', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Welcome back/ })).toBeVisible();
  await page.keyboard.press('g');
  await page.keyboard.press('d');
  await expect(page).toHaveURL(/\/dcf/);
  await page.keyboard.press('?');
  await expect(page.getByRole('dialog').getByText('Keyboard shortcuts')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('the palette also finds actions and files', async ({ page }) => {
  await page.goto('/upload');
  await page.locator('input[type=file]').setInputFiles({ name: 'palette-find-me.csv', mimeType: 'text/csv', buffer: Buffer.from('Item,2024,2025\nRevenue,1,2\n') });
  await expect(page.getByRole('button', { name: /palette-find-me\.csv/ }).first()).toBeVisible();
  await page.keyboard.press('Control+k');
  await page.getByRole('combobox', { name: 'Search pages' }).fill('palette-find');
  await expect(page.getByRole('option', { name: /palette-find-me\.csv/ }).first()).toBeVisible();
  await page.getByRole('combobox', { name: 'Search pages' }).fill('dark mode');
  await expect(page.getByRole('option', { name: /Switch to (dark|light) mode/ })).toBeVisible();
});

test('ratios show the DuPont breakdown of return on equity', async ({ page }) => {
  await page.goto('/ratios');
  await expect(page.getByRole('heading', { name: 'What drives return on equity' })).toBeVisible();
  await expect(page.getByText('equity multiplier').first()).toBeVisible();
});

test('short forms such as 2L are understood in number boxes', async ({ page }) => {
  await page.goto('/investment');
  await page.getByLabel('Initial investment (t = 0)').fill('2L');
  await expect(page.getByText('does not earn your required return')).toBeVisible();
});

test('an upload with a unit slip is flagged', async ({ page }) => {
  await page.goto('/upload');
  await page.locator('input[type=file]').setInputFiles({ name: 'unit-slip.csv', mimeType: 'text/csv', buffer: Buffer.from('Item,FY2023,FY2024,FY2025\nRevenue,1000,1100,1210000\nNet income,90,100,120\n') });
  await expect(page.getByText(/look unusual/)).toBeVisible();
  await expect(page.getByText(/factor of 500 or more in FY2025/)).toBeVisible();
});

test('a file dropped anywhere is analysed', async ({ page }) => {
  await page.goto('/ratios');
  await expect(page.getByRole('heading', { name: 'Overall reading' })).toBeVisible();
  await page.evaluate(() => {
    const dt = new DataTransfer();
    dt.items.add(new File(['Item,2024,2025\nRevenue,11000,12480\n'], 'dropped-anywhere.csv', { type: 'text/csv' }));
    for (const type of ['dragenter', 'dragover', 'drop']) window.dispatchEvent(new DragEvent(type, { dataTransfer: dt, bubbles: true, cancelable: true }));
  });
  await expect(page).toHaveURL(/\/upload\?file=/);
  await expect(page.getByText('dropped-anywhere.csv').first()).toBeVisible();
});

test('the background can be switched to still or off in Settings', async ({ page }) => {
  await page.goto('/settings');
  await page.getByRole('tab', { name: 'Still' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-backdrop', 'still');
  await page.getByRole('tab', { name: 'Off' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-backdrop', 'off');
  await page.getByRole('tab', { name: 'Moving' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-backdrop', 'animated');
});

test('scenarios open with a plain-English reading', async ({ page }) => {
  await page.goto('/scenarios');
  await expect(page.getByRole('heading', { name: 'In plain English' })).toBeVisible();
});

test('the cash budget opens with a plain-English reading', async ({ page }) => {
  await page.goto('/cash-flow');
  await page.getByRole('tab', { name: 'Cash budget & runway' }).click();
  await expect(page.getByRole('heading', { name: 'In plain English' })).toBeVisible();
});

test('a template fills the DCF with a worked example', async ({ page }) => {
  await page.goto('/dcf');
  await page.getByLabel('Start from a template').selectOption({ label: 'Start-up moving to profit' });
  await expect(page.getByText('These are illustrative starting numbers')).toBeVisible();
  await expect(page.getByText('In plain English').first()).toBeVisible();
});

test('the sample company gives a full dashboard in one click', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Try it with a sample company' }).click();
  await expect(page.getByText('Your data').first()).toBeVisible({ timeout: 20_000 });
  await expect(page.locator('select option', { hasText: 'Sample Co (fictional company)' })).toHaveCount(1);  // the company picker lists it
  await expect(page.getByText('Revenue (FY2025)')).toBeVisible();
  // clean up so other tests keep a new-account Overview
  const items = await (await page.request.get('/api/saved?kind=statements')).json();
  for (const i of items.items) await page.request.delete(`/api/saved/${i.id}`);
});

test('the month-end close checklist can be ticked, saved and reopened', async ({ page }) => {
  await page.goto('/close');
  await expect(page.getByRole('heading', { name: 'Month-end close' })).toBeVisible();
  await page.getByRole('checkbox', { name: /Done: Reconcile every bank/ }).check();
  await expect(page.getByText(/1 of \d+ done/).first()).toBeVisible();
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByLabel('Name').fill('E2E close');
  await page.getByRole('dialog').getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Saved "E2E close"')).toBeVisible();
  const items = await (await page.request.get('/api/saved?kind=checklist')).json();
  for (const i of items.items) await page.request.delete(`/api/saved/${i.id}`);
});

test('feedback can be sent from any page', async ({ page }) => {
  await page.goto('/ratios');
  await page.getByRole('button', { name: 'Send feedback' }).click();
  await page.getByLabel('Your note').fill('E2E: this is a test note');
  await page.getByRole('button', { name: 'Send', exact: true }).click();
  await expect(page.getByText('your note was sent')).toBeVisible();
});

test('the first Tab stop skips the menu and lands in the page', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Welcome back/ })).toBeVisible();
  await page.keyboard.press('Tab');
  const skip = page.getByRole('link', { name: 'Skip to main content' });
  await expect(skip).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
});

test('the compliance calendar lists dates, marks one filed and adds GST on request', async ({ page }) => {
  await page.goto('/calendar');
  await expect(page.getByRole('heading', { name: 'Compliance calendar' })).toBeVisible();
  const list = page.getByRole('list', { name: 'Compliance dates' });
  await expect(list.getByText('Last date to revise a return')).toBeVisible();
  await expect(list.getByText('GSTR-3B due')).toHaveCount(0);
  await list.getByRole('button', { name: 'Mark filed' }).last().click();
  await expect(list.getByRole('button', { name: 'Undo' })).toHaveCount(1);
  await page.getByLabel('Registered for GST?').selectOption('regular');
  await expect(list.getByText('GSTR-3B due').first()).toBeVisible();
});

test('show-me-how opens the working behind a figure', async ({ page }) => {
  await page.goto('/investment');
  await page.getByRole('button', { name: 'Show how Net present value is calculated' }).click();
  await expect(page.getByText('divided by (1 +')).toBeVisible();
});

test('the ratio readings can be judged against an industry', async ({ page }) => {
  await page.goto('/ratios');
  await expect(page.getByRole('heading', { name: 'Industry' })).toBeVisible();
  await page.getByLabel('Compare against').selectOption('utilities');
  await expect(page.getByLabel('Compare against')).toHaveValue('utilities');
});

test('the cash budget can charge interest and repay the loan', async ({ page }) => {
  await page.goto('/cash-flow');
  await page.getByRole('tab', { name: 'Cash budget & runway' }).click();
  await page.getByLabel('Interest on financing (% a year)').fill('12');
  await page.getByLabel('Repay financing from spare cash').check();
  await expect(page.getByText('Interest paid').first()).toBeVisible();
});

test('the DCF can step back and forward through changes', async ({ page }) => {
  await page.goto('/dcf');
  const undo = page.getByRole('button', { name: 'Undo the last change' });
  const redo = page.getByRole('button', { name: 'Redo the change you undid' });
  await expect(undo).toBeDisabled();
  const picker = page.getByLabel('Start from a template');
  const names = await picker.locator('option').allTextContents();
  await picker.selectOption({ index: 1 });
  await expect(page.getByText('Your assumptions')).toBeVisible();
  await expect(undo).toBeEnabled();
  await undo.click();
  await expect(page.getByText('Example assumptions')).toBeVisible();
  await expect(redo).toBeEnabled();
  await redo.click();
  await expect(page.getByText('Your assumptions')).toBeVisible();
  expect(names.length).toBeGreaterThan(1);
});

test('text size and high contrast apply at once and saved models export to Excel', async ({ page }) => {
  await page.goto('/settings');
  await page.getByRole('tab', { name: 'Large', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('data-textsize', 'large');
  await page.getByLabel(/High contrast/).check();
  await expect(page.locator('html')).toHaveAttribute('data-contrast', 'high');
  await page.getByRole('tab', { name: 'Normal', exact: true }).first().click();
  await page.getByLabel(/High contrast/).uncheck();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export saved models (Excel)' }).click();
  expect((await download).suggestedFilename()).toMatch(/\.xlsx$/);
  await expect(page.getByRole('heading', { name: 'Recent activity' })).toBeVisible();
});
