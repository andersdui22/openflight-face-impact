import { test, expect } from '@playwright/test';
import { gotoApp } from './helpers';

test('Gate 07 mobile viewport retains accessible session and camera navigation', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await page.getByRole('button', { name: 'OPEN FACE IMPACT DASHBOARD' }).click();
  const dashboard = page.getByRole('region', { name: 'Face Impact dashboard' });
  const sidebar = dashboard.getByLabel('Session and club sidebar');
  await expect(sidebar.getByRole('button', { name: /CURRENT SESSION/ })).toBeVisible();
  await expect(sidebar.getByRole('button', { name: 'CAMERA SETTINGS' })).toBeVisible();
  await expect(sidebar.getByRole('button', { name: 'SHOT HISTORY' })).toBeVisible();
  await expect(dashboard.getByRole('region', { name: 'Face Impact controls' })).toBeVisible();
});
