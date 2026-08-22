import { expect, test } from '@playwright/test';

for (const viewport of [{ width: 1440, height: 900 }, { width: 375, height: 812 }, { width: 320, height: 700 }]) {
  test(`Employee surface is reachable without page overflow at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Submit claim' })).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(1);
    await page.getByRole('button', { name: 'Submit claim' }).scrollIntoViewIfNeeded();
    await expect(page.getByRole('button', { name: 'Submit claim' })).toBeInViewport();
  });
}

test('every rendered form control has a programmatic accessible name', async ({ page }) => {
  await page.goto('/');
  const unnamed = await page.locator('button, input, select, textarea').evaluateAll((controls) => controls.filter((control) => {
    const element = control as HTMLInputElement;
    const labelled = element.getAttribute('aria-label') || element.getAttribute('aria-labelledby') || element.labels?.length || element.textContent?.trim();
    return !labelled;
  }).map((control) => control.outerHTML));
  expect(unnamed).toEqual([]);
});

test('keyboard focus is visible and dialogs return focus to the triggering action', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => { document.body.tabIndex = -1; document.body.focus(); });
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to workspace' })).toBeFocused();
  const deleteButton = page.getByRole('button', { name: 'Delete draft' });
  await deleteButton.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('dialog', { name: 'Delete this draft?' })).toBeVisible();
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(deleteButton).toBeFocused();
});

test('reduced-motion preference is honored by the task-owned stylesheet', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  expect(await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches)).toBe(true);
  const duration = await page.getByRole('button', { name: 'Employee workspace' }).evaluate((element) => getComputedStyle(element).animationDuration);
  expect(['0s', '0.00001s', '1e-05s']).toContain(duration);
});
