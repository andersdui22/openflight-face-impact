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

test('server-owned raster replay reaches only the requesting dashboard history', async ({ page, context }) => {
  await page.setViewportSize({ width: 1024, height: 768 });
  const openReview = async (view: import('@playwright/test').Page) => {
    await gotoApp(view);
    await view.getByRole('button', { name: 'Close Select club' }).click();
    await expect(view.getByLabel('Server connected')).toBeVisible();
    await view.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
    return view.getByRole('region', { name: 'Offline synthetic impact review' });
  };
  const review = await openReview(page);
  const observer = await openReview(await context.newPage());
  const run = review.getByRole('button', { name: 'Run synthetic replay' });
  const content = page.locator('.impact-workspace__content');
  const side = await page.getByRole('region', { name: 'Side Impact' }).boundingBox();
  expect(side!.height).toBeGreaterThan(100);
  await page.mouse.move(side!.x + 10, side!.y + 30);
  await page.mouse.down();
  await page.mouse.move(side!.x + 10, side!.y + 5, { steps: 4 });
  await page.mouse.up();
  await expect.poll(() => content.evaluate((element) => element.scrollTop)).toBeGreaterThan(0);

  await run.click();
  await expect(review.getByText('Selected shot: synthetic-contact')).toBeVisible();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(1);
  await expect(observer.getByText('OFFLINE RESULTS: 0')).toBeVisible();

  await review.getByLabel('Synthetic replay case').selectOption('missing-ball');
  await run.click();
  await expect(review.getByText('Selected shot: synthetic-missing-ball')).toBeVisible();
  await expect(review.getByText('REJECTED:')).toBeVisible();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(0);
  await expect(review.getByText('OFFLINE RESULTS: 2 · SYNTHETIC ACCEPTED: 1')).toBeVisible();
  await expect(observer.getByText('OFFLINE RESULTS: 0')).toBeVisible();

  await review.getByRole('button', { name: /synthetic-contact/ }).click();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(1);
});
