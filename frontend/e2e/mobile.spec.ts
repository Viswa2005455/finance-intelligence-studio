import { expect, test } from '@playwright/test';
import { ALL_PAGES, AUTH_FILE } from './global-setup';

// Phone-sized screen: nothing may spill sideways, and wide tables keep their first column in view.
test.use({ storageState: AUTH_FILE });

for (const path of ALL_PAGES) {
  test(`${path} does not scroll sideways on a phone`, async ({ page }) => {
    await page.goto(path);
    await page.waitForLoadState('networkidle');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
  });
}

test('on a phone the DCF results come before the assumptions', async ({ page }) => {
  await page.goto('/dcf');
  const reading = await page.getByText('In plain English').boundingBox();
  const assumptions = await page.getByRole('heading', { name: 'Assumptions' }).boundingBox();
  expect(reading && assumptions && reading.y < assumptions.y).toBe(true);
});

test('wide tables keep the row label in view while scrolling', async ({ page }) => {
  await page.goto('/dcf');
  const first = page.locator('.table-wrap table.data tbody tr').first().locator('td').first();
  await expect(first).toBeVisible();
  expect(await first.evaluate((el) => getComputedStyle(el).position)).toBe('sticky');
});
