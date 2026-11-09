import { test, expect } from '@playwright/test';
import { gotoApp } from './helpers';

async function openSyntheticDebug(page: import('@playwright/test').Page) {
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await expect(page.getByLabel('Server connected')).toBeVisible();
  await page.getByRole('button', { name: 'Debug' }).click();
  await expect(page.getByLabel('Synthetic Face Impact test case')).toBeVisible();
  // The demo can mount before the asynchronous Socket.IO handshake completes.
  await page.getByRole('button', { name: 'Request synthetic result' }).click();
}

test('real React Socket.IO client receives synthetic successes and rejections from Python', async ({ page }) => {
  await openSyntheticDebug(page);
  const preview = page.locator('section[aria-label="Synthetic Face Impact"]');
  const cases = page.getByLabel('Synthetic Face Impact test case');

  await expect(preview.getByText('X: 12.0 mm')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);

  await cases.selectOption('heel-low');
  await expect(preview.getByText('X: -12.0 mm')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);

  await cases.selectOption('outside-face');
  await expect(preview.getByText('Contact outside clubface')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(0);

  await cases.selectOption('no-tangency');
  await expect(preview.getByText('No ball-to-face contact')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(0);
});

test('real React client reports offline errors and recovers after reconnection', async ({ page, context }) => {
  await openSyntheticDebug(page);
  const preview = page.locator('section[aria-label="Synthetic Face Impact"]');
  await expect(preview.getByText('X: 12.0 mm')).toBeVisible();

  await context.setOffline(true);
  await expect(page.getByLabel('Server disconnected')).toBeVisible();
  await page.getByRole('button', { name: 'Request synthetic result' }).click();
  await expect(page.getByRole('alert').getByText('OpenFlight backend is disconnected')).toBeVisible();
  await expect(preview).toHaveCount(0);

  await context.setOffline(false);
  await expect(page.getByLabel('Server connected')).toBeVisible();
  await page.getByRole('button', { name: 'Request synthetic result' }).click();
  await expect(preview.getByText('X: 12.0 mm')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);
});
