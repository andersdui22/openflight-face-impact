import { expect, test } from '@playwright/test';
import { gotoApp } from './helpers';

test('configures the diagnostic camera and exports buffered host-timed frames', async ({ page }, info) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await gotoApp(page);
  const close = page.getByRole('button', { name: 'Close Select club' });
  if (await close.isVisible()) await close.click();
  await page.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
  const setup = page.getByLabel('Face Impact camera setup');
  await setup.getByText('Camera setup and diagnostics').click();
  await setup.getByLabel('Requested resolution').selectOption('640x400');
  await setup.getByLabel('Exposure (driver units)').fill('-6');
  await setup.getByLabel('Gain (driver units)').fill('10');
  await setup.getByLabel('Frames before trigger').fill('4');
  await setup.getByLabel('Frames after trigger').fill('5');
  await setup.getByLabel('Capture purpose').selectOption('checkerboard');
  await setup.getByRole('button', { name: 'Start or reconnect fixture' }).click();
  try {
    await expect(setup.getByText('fixture · fixture_match')).toBeVisible({ timeout: 11000 });
    await expect(setup.getByText('640 × 400', { exact: true })).toBeVisible({ timeout: 11000 });
    await expect(setup.getByText('Host arrival only · independent exposure timing unavailable')).toBeVisible();
    const [recording] = await Promise.all([
      page.waitForEvent('download'),
      setup.getByRole('button', { name: 'Record and export diagnostic' }).click(),
    ]);
    expect(recording.suggestedFilename()).toBe('face-impact-diagnostic.zip');
    await expect(setup.getByText('Diagnostic capture exported', { exact: false })).toBeVisible();
    const screenshot = info.outputPath('camera-setup.png');
    await setup.screenshot({ path: screenshot });
    await info.attach('camera-setup', { path: screenshot, contentType: 'image/png' });
  } finally {
    await setup.getByRole('button', { name: 'Stop fixture' }).click();
  }
});
