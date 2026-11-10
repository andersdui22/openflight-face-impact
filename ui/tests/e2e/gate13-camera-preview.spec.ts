import { expect, test } from '@playwright/test';
import { gotoApp } from './helpers';

async function openPreview(page: import('@playwright/test').Page) {
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await page.getByRole('button', { name: 'OPEN FACE IMPACT DASHBOARD' }).click();
  return page.getByRole('region', { name: 'Camera Preview' });
}

test('Gate 13 reports an absent backend without claiming a camera frame', async ({ page }) => {
  await page.route('**/api/camera/usb/status', (route) => route.abort());
  const preview = await openPreview(page);
  await expect(preview.getByText('Camera: offline')).toBeVisible();
  await expect(preview.locator('img')).toHaveCount(0);
  await expect(preview.getByText('USB preview only · no impact measurement')).toBeVisible();
});

test('Gate 13 shows a backend-reported stopped camera without requesting JPEG', async ({ page }) => {
  let jpegRequests = 0;
  await page.route('**/api/camera/usb/status', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ enabled: true, state: 'stopped' }) })
  );
  await page.route('**/api/camera/preview.jpg**', (route) => {
    jpegRequests += 1;
    return route.abort();
  });
  const preview = await openPreview(page);
  await expect(preview.getByText('Camera: stopped')).toBeVisible();
  await expect(preview.locator('img')).toHaveCount(0);
  expect(jpegRequests).toBe(0);
});

test('Gate 13 shows backend error detail without fabricating a preview', async ({ page }) => {
  await page.route('**/api/camera/usb/status', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ enabled: true, state: 'error', last_error: 'Mock USB driver unavailable' }),
    })
  );
  const preview = await openPreview(page);
  await expect(preview.getByText('Camera: error')).toBeVisible();
  await expect(preview.getByRole('alert')).toHaveText('Mock USB driver unavailable');
  await expect(preview.locator('img')).toHaveCount(0);
});

test('Gate 13 distinguishes an unavailable JPEG from a running camera status', async ({ page }) => {
  await page.route('**/api/camera/usb/status', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ enabled: true, state: 'running' }) })
  );
  await page.route('**/api/camera/preview.jpg**', (route) =>
    route.fulfill({ status: 503, contentType: 'text/plain', body: 'No buffered frame' })
  );
  const preview = await openPreview(page);
  await expect(preview.getByText('Camera preview unavailable')).toBeVisible();
  await expect(preview.getByText('USB preview only · no impact measurement')).toBeVisible();
});
