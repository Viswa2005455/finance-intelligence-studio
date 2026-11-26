import { expect, test } from '@playwright/test';

// Signed-out visitors: the overview, the no-sign-up demo, sign-in errors and password reset.

test('the overview explains the product and its demo calculator works without an account', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Analysis you can defend');
  await expect(page.getByText('Net present value')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'In plain English', exact: true })).toBeVisible();
  // Changing a number changes the answer: raise the required return until the project no longer pays.
  await page.getByLabel('Return you require each year').fill('30');
  await expect(page.getByText('Not worth doing')).toBeVisible();
  await expect(page.getByText('does not earn your required return')).toBeVisible();
});

test('a wrong password gives a plain message, not a server error', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Sign in' }).first().click();
  await page.getByLabel('Email').fill('nobody-here@example.com');
  await page.getByLabel('Password', { exact: true }).fill('not-the-password-1');
  await page.getByRole('button', { name: 'Sign in' }).last().click();
  await expect(page.getByText('Email or password is incorrect.')).toBeVisible();
  await expect(page.getByText('Internal error')).toHaveCount(0);
});

test('forgot password answers the same way for any address', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Sign in' }).first().click();
  await page.getByRole('button', { name: 'Forgot your password?' }).click();
  await page.getByLabel('Email').fill('nobody-here@example.com');
  await page.getByRole('button', { name: 'Send reset link' }).click();
  await expect(page.getByText('If an account exists for that email, a reset link is on its way.')).toBeVisible();
});

test('a reset link that is not valid is refused clearly', async ({ page }) => {
  await page.goto('/?reset=this-is-not-a-real-token');
  await expect(page.getByRole('heading', { name: 'Choose a new password' })).toBeVisible();
  await page.getByLabel('New password').fill('a-long-new-passphrase-1');
  await page.getByLabel('Type it again').fill('a-long-new-passphrase-1');
  await page.getByRole('button', { name: 'Change password' }).click();
  await expect(page.getByText('invalid or has expired')).toBeVisible();
});

test('private pages and calculators are not open to visitors', async ({ request }) => {
  const r = await request.post('/api/finance/appraisal', { data: { cash_flows: [-100, 60, 60], discount_rate: 0.1 } });
  expect(r.status()).toBe(401);
});
