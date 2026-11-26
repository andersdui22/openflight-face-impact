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

test('physical setup requires explicit activation and uses advertised native modes', async ({ page }, info) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  let starts = 0;
  let loads = 0;
  const modes = [
    { width: 1280, height: 800, numerator: 10_000_000, denominator: 83_333, format: 2, pixel_format: 'NV12' },
    { width: 1280, height: 800, numerator: 10_000_000, denominator: 83_333, format: 3, pixel_format: 'MJPG' },
    { width: 640, height: 480, numerator: 30, denominator: 1, format: 1, pixel_format: 'YUY2' },
  ];
  await page.route('**/api/face-impact/camera-setup/inventory', (route) =>
    route.fulfill({
      json: {
        devices: [{ identity: 'test-symbolic-link', name: 'Controlled camera entry', status: 'Media Foundation' }],
      },
    })
  );
  await page.route('**/api/face-impact/camera-setup/modes', (route) =>
    route.fulfill({
      json: { modes: loads++ === 0 ? modes : [...modes].reverse() },
    })
  );
  await page.route('**/api/face-impact/camera-setup/start', (route) => {
    expect(route.request().postDataJSON()).toMatchObject({
      identity: 'test-symbolic-link',
      activate_physical: true,
      mode: modes[starts++],
    });
    return route.fulfill({ status: 422, json: { error: 'Controlled test: no physical camera opened' } });
  });
  await gotoApp(page);
  const close = page.getByRole('button', { name: 'Close Select club' });
  if (await close.isVisible()) await close.click();
  await page.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
  const setup = page.getByLabel('Face Impact camera setup');
  await setup.getByText('Camera setup and diagnostics').click();
  await setup.getByRole('button', { name: 'Scan Windows cameras' }).click();
  await setup.getByLabel('Camera identity').selectOption('test-symbolic-link');
  await expect(setup.getByRole('button', { name: 'Load advertised modes' })).toBeDisabled();
  await expect(setup.getByRole('button', { name: 'Start or reconnect physical camera' })).toBeDisabled();
  await setup.getByLabel('Enable physical diagnostics').check();
  await setup.getByRole('button', { name: 'Load advertised modes' }).click();
  const modePicker = setup.getByLabel('Advertised camera mode');
  const load = setup.getByRole('button', { name: 'Load advertised modes' });
  await expect(modePicker).toHaveValue('1280:800:10000000:83333:2');
  await expect(modePicker.getByRole('option', { name: '1280 × 800 · 120 FPS · NV12' })).toHaveCount(1);
  await load.click();
  await expect(setup.getByText('Advertised native modes loaded.')).toBeVisible();
  await expect(modePicker).toHaveValue('1280:800:10000000:83333:2');
  expect(starts).toBe(0);
  const screenshot = info.outputPath('physical-camera-controls.png');
  await setup.screenshot({ path: screenshot });
  await info.attach('physical-camera-controls', { path: screenshot, contentType: 'image/png' });
  await setup.getByRole('button', { name: 'Start or reconnect physical camera' }).click();
  await expect(setup.getByRole('alert')).toHaveText('Controlled test: no physical camera opened');
  await modePicker.selectOption({ label: '1280 × 800 · 120 FPS · MJPG' });
  await setup.getByRole('button', { name: 'Start or reconnect physical camera' }).click();
  await expect(setup.getByRole('alert')).toHaveText('Controlled test: no physical camera opened');
  await modePicker.selectOption({ label: '640 × 480 · 30 FPS · YUY2' });
  await setup.getByRole('button', { name: 'Start or reconnect physical camera' }).click();
  await expect(setup.getByRole('alert')).toHaveText('Controlled test: no physical camera opened');
  expect(starts).toBe(3);
});
