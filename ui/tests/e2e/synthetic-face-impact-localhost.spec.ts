import { readFile } from 'node:fs/promises';
import { test, expect } from '@playwright/test';
import { gotoApp } from './helpers';

async function openSyntheticDebug(page: import('@playwright/test').Page) {
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await expect(page.getByLabel('Server connected')).toBeVisible();
  await page.getByRole('button', { name: 'Debug' }).click();
  await expect(page.getByLabel('Synthetic Face Impact test case')).toBeVisible();
}

test('real React Socket.IO client receives synthetic successes and rejections from Python', async ({ page }) => {
  await openSyntheticDebug(page);
  const preview = page.locator('section[aria-label="Synthetic Face Impact"]');
  const cases = page.getByLabel('Synthetic Face Impact test case');

  await expect(preview.getByText('X: 12.0 mm')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);

  await cases.selectOption('heel-low');
  await expect(preview.getByText('X: -12.0 mm')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);

  await cases.selectOption('outside-face');
  await expect(preview.getByText('Contact outside clubface')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(0);

  await cases.selectOption('no-tangency');
  await expect(preview.getByText('No ball-to-face contact')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(0);
});

test('real React client reports offline errors and recovers after reconnection', async ({ page, context }) => {
  await openSyntheticDebug(page);
  const preview = page.locator('section[aria-label="Synthetic Face Impact"]');
  await expect(preview.getByText('X: 12.0 mm')).toBeVisible();

  await context.setOffline(true);
  await expect(page.getByLabel('Server disconnected')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Request synthetic result' })).toBeDisabled();
  await expect(page.getByText('OpenFlight backend is disconnected')).toBeVisible();
  await expect(preview).toHaveCount(0);

  await context.setOffline(false);
  await expect(page.getByLabel('Server connected')).toBeVisible();
  await expect(page.getByText('OpenFlight backend is disconnected')).toHaveCount(0);
  await expect(preview.getByText('X: 12.0 mm')).toBeVisible();
  await expect(preview.getByTestId('synthetic-impact-marker')).toHaveCount(1);
});

test('server-owned raster replay reaches only the requesting dashboard history', async ({ page, context }) => {
  await page.setViewportSize({ width: 1024, height: 768 });
  const openReview = async (view: import('@playwright/test').Page) => {
    await gotoApp(view);
    await view.getByRole('button', { name: 'Close Select club' }).click();
    await expect(view.getByLabel('Server connected')).toBeVisible();
    await view.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
    return view.getByRole('region', { name: 'Offline synthetic impact review' });
  };
  const review = await openReview(page);
  const observer = await openReview(await context.newPage());
  const run = review.getByRole('button', { name: 'Run synthetic replay' });
  const content = page.locator('.impact-workspace__content');
  const side = await page.getByRole('region', { name: 'Side Impact' }).boundingBox();
  expect(side!.height).toBeGreaterThan(100);
  await page.mouse.move(side!.x + 10, side!.y + 30);
  await page.mouse.down();
  await page.mouse.move(side!.x + 10, side!.y + 5, { steps: 4 });
  await page.mouse.up();
  await expect.poll(() => content.evaluate((element) => element.scrollTop)).toBeGreaterThan(0);

  await run.click();
  await expect(review.getByText('Selected shot: synthetic-contact')).toBeVisible();
  await expect(review.getByText('Received from Python replay')).toBeVisible();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(1);
  await expect(observer.getByText('OFFLINE RESULTS: 0')).toBeVisible();

  await review.getByLabel('Synthetic replay case').selectOption('missing-ball');
  await run.click();
  await expect(review.getByText('Selected shot: synthetic-missing-ball')).toBeVisible();
  await expect(review.getByText('REJECTED:')).toBeVisible();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(0);
  await expect(review.getByText('OFFLINE RESULTS: 2 · SYNTHETIC ACCEPTED: 1')).toBeVisible();
  await expect(observer.getByText('OFFLINE RESULTS: 0')).toBeVisible();

  await review.getByRole('button', { name: /synthetic-contact/ }).click();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(1);
});

test('synthetic session can be reopened and exported with provenance', async ({ page }) => {
  const openReview = async () => {
    await gotoApp(page);
    await page.getByRole('button', { name: 'Close Select club' }).click();
    await expect(page.getByLabel('Server connected')).toBeVisible();
    await page.getByRole('button', { name: 'Open Face Impact dashboard' }).click();
    const review = page.getByRole('region', { name: 'Offline synthetic impact review' });
    await review.getByText('Saved synthetic sessions', { exact: true }).click();
    return review;
  };
  const review = await openReview();
  await review.getByRole('button', { name: 'Run in new session' }).click();
  await expect(review.getByText('OFFLINE RESULTS: 1 · SYNTHETIC ACCEPTED: 1')).toBeVisible();
  const selected = await review.getByText('Selected shot:').textContent();
  const sessionId = selected?.match(/Session: (synthetic-[a-f0-9]{32})/)?.[1];
  expect(sessionId).toBeTruthy();

  await review.getByLabel('Synthetic replay case').selectOption('missing-ball');
  await review.getByRole('button', { name: 'Run synthetic replay' }).click();
  await expect(review.getByText('OFFLINE RESULTS: 2 · SYNTHETIC ACCEPTED: 1')).toBeVisible();
  await expect(review.getByTestId('synthetic-impact-marker')).toHaveCount(0);

  const reopened = await openReview();
  await expect(reopened.getByText('OFFLINE RESULTS: 0')).toBeVisible();
  await reopened.getByLabel('Saved session', { exact: true }).selectOption(sessionId!);
  await reopened.getByRole('button', { name: 'Load session' }).click();
  await expect(reopened.getByText('Loaded from saved session')).toBeVisible();
  await expect(reopened.getByText('OFFLINE RESULTS: 2 · SYNTHETIC ACCEPTED: 1')).toBeVisible();
  await reopened.getByRole('button', { name: new RegExp(`${sessionId}-contact`) }).click();
  await expect(reopened.getByTestId('synthetic-impact-marker')).toHaveCount(1);
  for (const [replayCase, count] of [
    ['contact', 3],
    ['heel-contact', 4],
    ['compact-contact', 5],
  ] as const) {
    await reopened.getByLabel('Synthetic replay case').selectOption(replayCase);
    await reopened.getByRole('button', { name: 'Run synthetic replay' }).click();
    await expect(reopened.getByText(`OFFLINE RESULTS: ${count} · SYNTHETIC ACCEPTED: ${count - 1}`)).toBeVisible();
  }
  const analysis = reopened.getByRole('region', { name: 'Saved synthetic session analysis' });
  await expect(analysis.getByRole('img', { name: /Synthetic impact distribution/ })).toHaveCount(2);
  await analysis.getByLabel('Club model', { exact: true }).selectOption('synthetic-planar-face-v1');
  await expect(analysis.getByText('Saved shots 4 · Accepted 3 · Rejected 1')).toBeVisible();
  await expect(analysis.getByText(/Spread \(standard deviation\) X \d/)).toBeVisible();
  await expect(analysis.locator('svg title').filter({ hasText: '2 synthetic shots' })).toHaveCount(1);
  await expect(analysis.locator('svg title').filter({ hasText: 'Mean impact' })).toHaveCount(1);
  await analysis.getByText('Session diagnostics', { exact: true }).click();
  await expect(analysis.getByText('Synthetic rejected', { exact: true })).toBeVisible();
  await expect(analysis.getByText(/Sensor intervals/)).toHaveCount(4);

  const downloadPromise = page.waitForEvent('download');
  await reopened.getByRole('link', { name: 'Export session JSON' }).click();
  const download = await downloadPromise;
  const archive = JSON.parse(await readFile(await download.path(), 'utf8'));
  expect(archive.session_id).toBe(sessionId);
  expect(archive.shots).toHaveLength(5);
  expect(new Set(archive.shots.map((shot: { evidence: { shot_id: string } }) => shot.evidence.shot_id)).size).toBe(5);
  const [accepted, rejected] = archive.shots;
  expect(accepted.evidence.accepted).toBe(true);
  expect(accepted.provenance.calibration.id).toBe('synthetic-brown-five-v1');
  expect(accepted.provenance.capture.frames).toHaveLength(2);
  expect(rejected.evidence.accepted).toBe(false);
  expect(rejected.evidence).not.toHaveProperty('x_mm');
  expect(archive.analysis.clubs).toHaveLength(2);
  const planar = archive.analysis.clubs.find(
    (club: { club_id: string }) => club.club_id === 'synthetic-planar-face-v1'
  );
  const points = archive.shots
    .filter((shot: typeof accepted) => shot.evidence.accepted && shot.provenance.club.model_id === planar.club_id)
    .map((shot: typeof accepted) => [shot.evidence.x_mm, shot.evidence.y_mm]);
  for (const axis of [0, 1]) {
    const mean = points.reduce((sum: number, point: number[]) => sum + point[axis], 0) / points.length;
    const variance =
      points.reduce((sum: number, point: number[]) => sum + (point[axis] - mean) ** 2, 0) / points.length;
    expect(planar.mean_mm[axis]).toBeCloseTo(mean, 8);
    expect(planar.spread_mm[axis]).toBeCloseTo(Math.sqrt(variance), 8);
  }
  expect(archive.analysis.diagnostics.map((shot: { status: string }) => shot.status)).toContain('rejected');
});
