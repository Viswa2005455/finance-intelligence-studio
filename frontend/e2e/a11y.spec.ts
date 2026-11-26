import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';
import { AUTH_FILE } from './global-setup';

/** Automated accessibility check (WCAG 2.0/2.1 A and AA). It fails on serious and critical problems; minor ones are listed in the log. */
async function audit(page: Page, name: string) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
  const bad = results.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
  for (const v of results.violations) {
    console.log(`[a11y] ${name}: ${v.impact} ${v.id} (${v.nodes.length}) ${v.help}`);
    for (const n of v.nodes.slice(0, 3)) {
      const d = n.any[0]?.data as { fgColor?: string; bgColor?: string; contrastRatio?: number } | undefined;
      console.log(`         ${n.target.join(' ')} ${d?.fgColor ? `fg ${d.fgColor} on ${d.bgColor} = ${d.contrastRatio}` : ''}`);
    }
  }
  expect(bad.map((v) => `${v.id}: ${v.help} -> ${v.nodes.slice(0, 2).map((n) => n.target.join(' ')).join(' | ')}`), `${name} has serious accessibility problems`).toEqual([]);
}

test.describe('signed out', () => {
  test('overview', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Net present value')).toBeVisible();
    await audit(page, 'overview');
  });
  test('sign in', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign in' }).first().click();
    await audit(page, 'sign in');
  });
});

test.describe('signed in', () => {
  test.use({ storageState: AUTH_FILE });
  for (const [path, ready] of [['/', 'Get started'], ['/ratios', 'Overall reading'], ['/dcf', 'In plain English'], ['/budgeting', 'Budgeted revenue'], ['/upload', 'Drop files here'], ['/investment', 'In plain English']] as const) {
    test(path, async ({ page }) => {
      await page.goto(path);
      await expect(page.getByText(ready).first()).toBeVisible();
      await audit(page, path);
    });
  }
});
