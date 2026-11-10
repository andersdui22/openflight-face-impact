import { test, expect } from '@playwright/test';
import { gotoApp } from './helpers';

test('Gate 07 setup controls are keyboard accessible and UI-only', async ({ page }) => {
  await gotoApp(page);
  const picker = page.getByRole('dialog', { name: 'Select club' });
  if (await picker.isVisible()) {
    await page.getByRole('button', { name: 'Close Select club' }).click();
  }
  await page.getByRole('button', { name: 'OPEN FACE IMPACT DASHBOARD' }).click();
  const controls = page.getByRole('region', { name: 'Face Impact controls' });

  const handedness = controls.getByRole('combobox', { name: 'Handedness' });
  await expect(handedness).toHaveValue('right');
  await handedness.selectOption('left');
  await expect(handedness).toHaveValue('left');

  const cameraPosition = controls.getByRole('combobox', { name: 'Camera position' });
  await cameraPosition.selectOption('top');
  await expect(cameraPosition).toHaveValue('top');

  const overlay = controls.getByRole('checkbox', { name: /Show alignment overlay/ });
  await expect(overlay).toBeChecked();
  await overlay.uncheck();
  await expect(overlay).not.toBeChecked();

  const calibration = controls.getByRole('button', { name: 'Calibration' });
  await calibration.focus();
  await expect(calibration).toBeFocused();
  await expect(calibration).toHaveCSS('outline-style', 'solid');
  await page.keyboard.press('Enter');
  await expect(calibration).toHaveAttribute('aria-pressed', 'true');
  await expect(controls.getByRole('button', { name: /START CALIBRATION/ })).toBeDisabled();

  const setup = controls.getByRole('button', { name: 'Camera setup' });
  await setup.focus();
  await page.keyboard.press('Space');
  await expect(setup).toHaveAttribute('aria-pressed', 'true');
  await expect(controls.getByRole('combobox', { name: 'Handedness' })).toHaveValue('left');
  await expect(controls.getByRole('combobox', { name: 'Camera position' })).toHaveValue('top');
  await expect(controls.getByRole('checkbox', { name: /Show alignment overlay/ })).not.toBeChecked();
  await expect(controls.getByText(/Settings are local to this view and are not saved/)).toBeVisible();
});
