import { test, expect } from '@playwright/test';
import { gotoApp } from './helpers';

test('Gate 07 visual dashboard preserves six panels and exposes honest UI-only controls', async ({ page }, testInfo) => {
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }

  await page.getByRole('button', { name: 'OPEN FACE IMPACT DASHBOARD' }).click();
  const dashboard = page.getByRole('region', { name: 'Face Impact dashboard' });
  for (const title of [
    'Side Impact',
    'Front Impact',
    'Top Impact',
    'Impact Distribution',
    'Camera Preview',
    'Shot Replay',
  ]) {
    await expect(dashboard.getByRole('region', { name: title })).toBeVisible();
  }

  const controls = dashboard.getByRole('region', { name: 'Face Impact controls' });
  await expect(controls.getByText('No camera measurements are active.')).toBeVisible();
  await expect(controls.getByRole('button', { name: /CONNECT CAMERA/ })).toBeDisabled();
  await controls.getByRole('button', { name: 'Calibration' }).click();
  await expect(controls.getByRole('button', { name: /START CALIBRATION/ })).toBeDisabled();
  await controls.getByRole('button', { name: 'Capture' }).click();
  await expect(controls.getByRole('button', { name: /START CAPTURE/ })).toBeDisabled();
  await controls.getByRole('button', { name: 'Replay' }).click();
  await expect(controls.getByRole('button', { name: /PLAY/ })).toBeDisabled();
  await controls.getByRole('button', { name: 'Camera setup' }).click();

  await testInfo.attach('gate07-real-browser-dashboard', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png',
  });
});
