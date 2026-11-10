import { test, expect } from '@playwright/test';
import { gotoApp } from './helpers';

test('Gate 09 demo session is isolated from measured shots and can be reset', async ({ page }) => {
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await page.getByRole('button', { name: 'OPEN FACE IMPACT DASHBOARD' }).click();
  const dashboard = page.getByRole('region', { name: 'Face Impact dashboard' });
  const demo = dashboard.getByRole('region', { name: 'Face Impact simulated session' });
  const distribution = dashboard.getByRole('region', { name: 'Impact Distribution' });

  await expect(demo.getByText('SIMULATED SESSION — DEMO ONLY')).toBeVisible();
  await expect(demo.getByText(/Not camera measurements or recorded shots/)).toBeVisible();
  const add = demo.getByRole('button', { name: 'ADD SIMULATED SHOT' });
  const reset = demo.getByRole('button', { name: 'RESET DEMO SESSION' });
  await expect(add).toBeDisabled();
  await expect(reset).toBeDisabled();

  await demo.getByRole('button', { name: 'ENTER DEMO MODE' }).click();
  await expect(demo.getByRole('status')).toContainText('SIMULATED SHOTS: 0');
  await expect(distribution.getByRole('img', { name: 'DEMO ONLY impact map with 0 simulated shots' })).toBeVisible();
  await add.click();
  await expect(demo.getByRole('listitem')).toContainText(['SIMULATED SHOT 1: X -12 mm, Y 8 mm']);
  await expect(demo.getByRole('status')).toContainText('AVERAGE X: -12.0 mm');
  await add.click();
  await expect(demo.getByRole('listitem')).toHaveCount(2);
  await expect(distribution.getByRole('img', { name: 'DEMO ONLY impact map with 2 simulated shots' })).toBeVisible();
  await expect(distribution.locator('svg circle')).toHaveCount(2);
  await expect(demo.getByRole('status')).toContainText('AVERAGE X: -2.5 mm');
  await expect(demo.getByRole('status')).toContainText('AVERAGE Y: 1.5 mm');

  await expect(dashboard.getByRole('region', { name: 'Face Impact metrics' }).getByText('not measured').first()).toBeVisible();
  await reset.click();
  await expect(demo.getByRole('listitem')).toHaveCount(0);
  await expect(distribution.locator('svg circle')).toHaveCount(0);
  await expect(demo.getByRole('status')).toContainText('SIMULATED SHOTS: 0');
  await expect(reset).toBeDisabled();
  await demo.getByRole('button', { name: 'EXIT DEMO MODE' }).click();
  await expect(add).toBeDisabled();
  await expect(demo.getByRole('status')).toHaveCount(0);
});
