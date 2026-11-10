// Kiosk shell for the OpenFlight React UI. Loads whatever URL the launcher
// script gives it (the startup splash, then the app itself once it
// navigates there) in a chromeless, fullscreen window — this replaces
// scripts/start-kiosk.sh's old system-browser detection (chromium-browser /
// chromium / google-chrome / firefox) with one pinned Chromium version.

import { app, BrowserWindow, Menu } from 'electron';
import { fileURLToPath } from 'node:url';
import { existsSync, writeFileSync } from 'node:fs';
import { resolveTargetUrl } from './resolveTargetUrl.js';

const targetUrl = resolveTargetUrl(process.env, process.argv);

Menu.setApplicationMenu(null);

function createWindow() {
  const win = new BrowserWindow({
    kiosk: true,
    fullscreen: true,
    autoHideMenuBar: true,
    backgroundColor: '#000000',
    webPreferences: {
      contextIsolation: true,
      sandbox: true,
    },
  });

  win.setMenuBarVisibility(false);
  // The kiosk shell only ever shows the OpenFlight UI itself; deny any
  // attempt (e.g. target="_blank" links) to pop a second window.
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  if (app.isPackaged || process.env.OPENFLIGHT_PORTABLE === '1' || (!process.defaultApp && existsSync(fileURLToPath(new URL('../dist/index.html', import.meta.url))))) {
    // The portable Windows bundle starts its bundled UI without a terminal or server.
    // Hardware/backend features remain unavailable until a supported service is connected.
    win.loadFile(fileURLToPath(new URL('../dist/index.html', import.meta.url)));
  } else {
    win.loadURL(targetUrl);
  }

  // Gate 11 CI-only smoke: exercise the actual packaged renderer and capture evidence.
  // Disabled for ordinary users. Never activates a camera or measurement.
  if (process.env.OPENFLIGHT_GATE11_SMOKE === '1') {
    win.webContents.once('did-finish-load', async () => {
      try {
        const result = await win.webContents.executeJavaScript(`
          (async () => {
            const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
            for (let i = 0; i < 60; i++) {
              const button = [...document.querySelectorAll('button')]
                .find((item) => item.textContent?.includes('OPEN FACE IMPACT DASHBOARD'));
              if (button) {
                button.click();
                await sleep(500);
                const dashboard = document.querySelector('[aria-label="Face Impact dashboard"]');
                const panels = ['Side Impact', 'Front Impact', 'Top Impact',
                  'Impact Distribution', 'Camera Preview', 'Shot Replay'];
                if (dashboard && panels.every((name) => dashboard.querySelector(
                  '[aria-label="' + name + '"]'))) {
                  return { ok: true, panels: panels.length };
                }
              }
              await sleep(500);
            }
            return { ok: false, error: 'Dashboard or six panels not rendered' };
          })()
        `);
        if (!result.ok) throw new Error(result.error);
        const shot = await win.webContents.capturePage();
        writeFileSync(process.env.OPENFLIGHT_GATE11_SCREENSHOT, shot.toPNG());
        writeFileSync(process.env.OPENFLIGHT_GATE11_RESULT, JSON.stringify(result));
        app.exit(0);
      } catch (error) {
        writeFileSync(process.env.OPENFLIGHT_GATE11_RESULT, JSON.stringify({
          ok: false, error: String(error),
        }));
        app.exit(1);
      }
    });
  }

  win.on('closed', () => {
    app.quit();
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  app.quit();
});
