import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Reset simulated workspace' }).click();
});

test('Employee submits a clean valid draft through the public surface', async ({ page }) => {
  await page.getByRole('button', { name: 'Submit claim' }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Claim submitted.' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'clm-draft · Submitted' })).toBeVisible();
  await expect(page.getByText('Revision 1 is read-only')).toBeVisible();
});

test('Manager approves the exact displayed revision', async ({ page }) => {
  await page.getByRole('button', { name: 'Manager workspace' }).click();
  await page.getByRole('button', { name: 'clm-submitted · Submitted' }).click();
  await expect(page.getByText('Exact review target: revision 1 · version 1')).toBeVisible();
  await page.getByRole('button', { name: 'Approve revision 1' }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Claim approved for payment.' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'clm-submitted · Payment pending' })).toBeVisible();
});

test('Manager queue excludes self-review and out-of-scope lifecycle states', async ({ page }) => {
  await page.getByRole('button', { name: 'Manager workspace' }).click();
  await expect(page.getByRole('button', { name: 'clm-submitted · Submitted' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'clm-approved · Payment pending' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'clm-self-review · Submitted' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'clm-draft · Draft' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'clm-completed · Payment completed' })).toHaveCount(0);
});

test('Finance atomically claims and schedules shared payment work', async ({ page }) => {
  await page.getByRole('button', { name: 'Finance workspace' }).click();
  await page.getByRole('button', { name: 'clm-approved · Payment pending' }).click();
  await page.getByRole('button', { name: 'Claim and schedule payment' }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Payment claimed and scheduled.' })).toBeVisible();
  await expect(page.getByText('Owner: Finance Kim')).toBeVisible();
  await expect(page.getByRole('button', { name: 'clm-approved · Scheduled' })).toBeVisible();
});

test('Admin deactivates an account and exposes the new authorization version', async ({ page }) => {
  await page.getByRole('button', { name: 'Admin workspace' }).click();
  await page.getByRole('tab', { name: 'Accounts & roles' }).click();
  await page.getByRole('combobox', { name: 'Managed user' }).selectOption('usr-employee');
  await page.getByRole('textbox', { name: 'Account change reason' }).fill('Employment ended');
  await page.getByRole('button', { name: 'Deactivate account' }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Account and roles updated; active sessions invalidated.' })).toBeVisible();
  await expect(page.getByText('Inactive · auth version 2')).toBeVisible();
});
