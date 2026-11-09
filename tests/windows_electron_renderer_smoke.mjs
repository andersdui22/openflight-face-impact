import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(new URL('../ui/package.json', import.meta.url));
const { chromium, expect } = require('@playwright/test');
const [debugPort, appUrl] = process.argv.slice(2);

const browser = await chromium.connectOverCDP(`http://127.0.0.1:${debugPort}`, {
  timeout: 15_000,
});
try {
  const pages = () => browser.contexts().flatMap((context) => context.pages());
  await expect.poll(() => pages().some((page) => page.url() === appUrl), {
    timeout: 20_000,
  }).toBe(true);
  const page = pages().find((candidate) => candidate.url() === appUrl);

  const picker = page.getByRole('dialog', { name: 'Select club' });
  await expect(page.getByLabel('Server connected')).toBeVisible({ timeout: 15_000 });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await page.getByRole('button', { name: 'Debug', exact: true }).click({ timeout: 10_000 });
  await page.getByRole('button', { name: 'Request synthetic result' }).click({ timeout: 10_000 });

  const preview = page.locator('section[aria-label="Synthetic Face Impact"]');
  await expect(preview.getByText('X: 12.0 mm')).toBeVisible({ timeout: 10_000 });
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);
  console.log('Electron rendered OpenFlight and displayed a synthetic Face Impact result');

  await page.close({ runBeforeUnload: false });
  assert.equal(page.isClosed(), true, 'OpenFlight window did not close');
} finally {
  await browser.close();
}
