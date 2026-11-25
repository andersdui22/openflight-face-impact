import { expect, test } from '@playwright/test';
import { gotoApp } from './helpers';

test('downloads, imports and replays a recording with its independent receipt', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  async function openRegister() {
    await gotoApp(page);
    const close = page.getByRole('button', { name: 'Close Select club' });
    if (await close.isVisible()) await close.click();
    await page.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
    await page.getByText('Import and replay recordings', { exact: true }).click();
    return page.getByLabel('Recorded synthetic captures');
  }
  let register = await openRegister();
  const [sample] = await Promise.all([
    page.waitForEvent('download'),
    register.getByRole('button', { name: 'Download synthetic sample' }).click(),
  ]);
  const zip = testInfo.outputPath('sample.zip');
  await sample.saveAs(zip);
  await register.getByLabel('Recording ZIP').setInputFiles(zip);
  await register.getByRole('button', { name: 'Import recording' }).click();
  await expect(register.getByText('Independent synthetic receipt matched')).toBeVisible();
  await register.getByRole('button', { name: 'Replay recording' }).click();
  await expect(register.getByText('Synthetic replay accepted and saved to session history.')).toBeVisible();
  await expect(page.getByText('Loaded from saved session')).toBeVisible();
  await register.scrollIntoViewIfNeeded();
  const screenshot = testInfo.outputPath('recording-import.png');
  await register.screenshot({ path: screenshot });
  await testInfo.attach('recording-import', { path: screenshot, contentType: 'image/png' });

  register = await openRegister();
  await expect(register.getByText('Independent synthetic receipt matched')).toBeVisible();
  await register.getByRole('button', { name: 'Replay recording' }).click();
  await expect(register.getByText('Synthetic replay accepted and saved to session history.')).toBeVisible();
  await page.getByText('Saved synthetic sessions', { exact: true }).click();
  await expect(page.getByRole('link', { name: 'Export session JSON' })).toBeVisible();
});
