import { expect, test } from '@playwright/test';
import { gotoApp } from './helpers';

// Visual evidence of the React USB-status presentation, not a physical camera test.
// The real OpenFlight frontend and browser run against the existing mock backend.
test('renders Windows USB camera status and captures genuine browser evidence', async ({ page }, testInfo) => {
  await page.route('**/api/camera/usb/status', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ enabled: true, state: 'starting', frames_received: 0 }),
    });
  });

  await gotoApp(page);
  await page.getByRole('button', { name: 'Close Select club' }).click();
  await page.evaluate(
    "import('/src/stores/useCameraStore.ts').then(({ useCameraStore }) => " +
      'useCameraStore.getState().setCaptureSettings({ available: true, enabled: true, running: true }))'
  );
  await page.getByRole('button', { name: 'Camera' }).click();

  const status = page.getByRole('status', { name: '' }).filter({ hasText: 'USB: starting' });
  await expect(status).toBeVisible();
  await expect(page.getByText('Auto exposure:', { exact: false })).toHaveCount(0);

  await testInfo.attach('gate03-usb-status-browser', {
    body: await page.screenshot({ fullPage: true, animations: 'disabled' }),
    contentType: 'image/png',
  });
});
