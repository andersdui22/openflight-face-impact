import { expect, test } from '@playwright/test';
import { gotoApp } from './helpers';

const backend = 'http://127.0.0.1:8080';

test('one USB adapter supplies preview and trigger across fixture recovery', async ({ page, request }) => {
  const control = (action: string) =>
    request.post(`${backend}/api/test/usb-camera/${action}`, {
      headers: { 'X-OpenFlight-Smoke': 'usb-fixture' },
    });
  const status = async () => (await request.get(`${backend}/api/camera/usb/status`)).json();

  await gotoApp(page);
  await page.getByRole('button', { name: 'Close Select club' }).click();
  await page.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
  const preview = page.getByLabel('USB camera preview');
  const image = preview.getByRole('img');
  await expect.poll(() => image.evaluateAll((elements: HTMLImageElement[]) => elements[0]?.naturalWidth), { timeout: 10000 }).toBe(96);
  expect(await status()).toMatchObject({
    state: 'running',
    delivered_size: [96, 64],
    negotiated: { width: 640, height: 400 },
    timestamp_source: 'host_arrival_monotonic',
    calibration: { state: 'mode_unknown', physical_validation: false },
  });

  const capture = await control('trigger');
  expect(capture.ok()).toBeTruthy();
  expect(await capture.json()).toEqual({
    frame_sizes: [[96, 64], [96, 64]],
    pixel_levels: [32, 32],
    host_clock_aliases: [true, true],
    rejection: 'independent sensor timestamp unavailable',
  });

  expect((await control('disconnect')).ok()).toBeTruthy();
  await expect(preview.getByRole('alert')).toHaveText(/disconnected/, { timeout: 10000 });
  await expect(image).toHaveCount(0);
  expect((await request.get(`${backend}/api/camera/preview.jpg`)).status()).toBe(503);
  expect((await control('trigger')).status()).toBe(409);
  expect(await status()).toMatchObject({ state: 'error', delivered_size: null });

  expect(await (await control('restart')).json()).toEqual({ previous_handle_released: true });
  await expect.poll(() => image.evaluateAll((elements: HTMLImageElement[]) => elements[0]?.naturalWidth), { timeout: 10000 }).toBe(80);
  await expect(preview.getByRole('alert')).toHaveCount(0);
  await expect(preview.getByLabel('Camera calibration status')).toHaveText(
    'Calibration profile incompatible with camera mode',
  );
  expect(await status()).toMatchObject({
    state: 'running',
    delivered_size: [80, 48],
    calibration: { state: 'mode_incompatible', physical_validation: false },
  });
  await expect(page.getByText('No measured impacts yet')).toBeVisible();

  const recovered = await control('trigger');
  expect(await recovered.json()).toMatchObject({
    frame_sizes: [[80, 48], [80, 48]],
    pixel_levels: [64, 64],
    host_clock_aliases: [true, true],
  });
  expect((await control('invalid')).ok()).toBeTruthy();
  await expect(preview.getByRole('alert')).toHaveText('unsupported USB frame format', { timeout: 10000 });
  await expect(image).toHaveCount(0);
  expect(await (await control('restart')).json()).toEqual({ previous_handle_released: true });
});
