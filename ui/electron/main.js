// Kiosk shell for the OpenFlight React UI. Loads whatever URL the launcher
// script gives it (the startup splash, then the app itself once it
// navigates there) in a chromeless, fullscreen window — this replaces
// scripts/start-kiosk.sh's old system-browser detection (chromium-browser /
// chromium / google-chrome / firefox) with one pinned Chromium version.

import { app, BrowserWindow, Menu } from 'electron';
import { fileURLToPath } from 'node:url';
import { existsSync, writeFileSync } from 'node:fs';
import { resolveTargetUrl } from './resolveTargetUrl.js';
import { resolveBackendExecutable, startBackend, stopBackend, waitForBackendReady } from './backendProcess.js';

const targetUrl = resolveTargetUrl(process.env, process.argv);

Menu.setApplicationMenu(null);

let backendChild = null;
let backendStartupError = null;
let backendReady = false;

async function launchOptInBackend() {
  try {
    const executable = resolveBackendExecutable(process.env, app.isPackaged ? process.resourcesPath : null);
    backendChild = startBackend(executable, {
      onError: (error) => { backendStartupError = error; console.error(error); },
    });
    if (backendChild) {
      backendReady = await waitForBackendReady({
        isRunning: () => backendChild.exitCode === null && !backendChild.killed && !backendStartupError,
      });
      if (!backendReady) console.error("Face Impact backend readiness check failed");
    }
  } catch (error) {
    backendStartupError = error;
    console.error(error);
  }
}

// Exercise the real portable renderer in CI with either the mock backend or
// the UI-only bundle. The club picker must be closed before taking a screenshot.
async function runDashboardSmoke(win) {
  const expectsBackend = process.env.OPENFLIGHT_GATE11_EXPECT_BACKEND === '1';
  const resultPath = process.env.OPENFLIGHT_GATE11_RESULT;
  try {
    if (backendReady !== expectsBackend) {
      throw new Error(`Expected mock backend ready=${expectsBackend}, got ${backendReady}`);
    }
    const result = await win.webContents.executeJavaScript(`
      (async (expectsBackend) => {
        const waitFor = async (predicate, message) => {
          for (let attempt = 0; attempt < 100; attempt++) {
            const value = predicate();
            if (value) return value;
            await new Promise((resolve) => setTimeout(resolve, 100));
          }
          throw new Error(message);
        };
        const open = await waitFor(() => document.querySelector('.impact-workspace__return'),
          'Dashboard entry button not rendered');
        document.querySelector('button[aria-label="Close Select club"]')?.click();
        await waitFor(() => !document.querySelector('[role="dialog"][aria-label="Select club"]'),
          'Club picker still obscures the dashboard');
        if (expectsBackend) {
          await waitFor(() => document.querySelector('[aria-label="Server connected"]'),
            'Packaged renderer did not connect to the mock backend');
        }
        open.click();
        const dashboard = await waitFor(() => document.querySelector('[aria-label="Face Impact dashboard"]'),
          'Dashboard not rendered');
        const panels = ['Side Impact', 'Front Impact', 'Top Impact', 'Impact Distribution',
          'Camera Preview', 'Shot Replay'];
        if (!panels.every((name) => dashboard.querySelector('[aria-label="' + name + '"]'))) {
          throw new Error('Expected six dashboard panels');
        }
        const preview = dashboard.querySelector('[aria-label="USB camera preview"]');
        const cameraStatus = expectsBackend ? 'Camera: disabled' : 'Camera: offline';
        await waitFor(() => preview?.textContent.includes(cameraStatus), 'Expected ' + cameraStatus);
        const marker = () => dashboard.querySelector('[data-testid="synthetic-impact-marker"]');
        if (expectsBackend) {
          await waitFor(marker, 'Mock backend did not render a synthetic impact marker');
          const review = dashboard.querySelector('[aria-label="Offline synthetic impact review"]');
          const replay = Array.from(review?.querySelectorAll('button') ?? [])
            .find((button) => button.textContent === 'Run synthetic replay');
          if (!replay) throw new Error('Offline replay button not rendered');
          replay.click();
          await waitFor(() => review.textContent.includes('synthetic-contact') &&
            review.querySelector('[data-testid="synthetic-impact-marker"]'),
            'Mock backend did not deliver offline raster evidence');
          review.scrollIntoView({ block: 'start' });
        } else {
          await waitFor(() => dashboard.textContent.includes('OpenFlight backend is disconnected'),
            'UI did not report the disconnected backend');
          if (marker()) throw new Error('Disconnected dashboard displayed a synthetic marker');
        }
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        return { ok: true, panels: panels.length, backend_ready: expectsBackend, camera: cameraStatus };
      })(${JSON.stringify(expectsBackend)})
    `);
    const shot = await win.webContents.capturePage();
    const { width, height } = shot.getSize();
    if (width < 800 || height < 400) {
      throw new Error(`Dashboard capture has invalid dimensions ${width}x${height}`);
    }
    writeFileSync(process.env.OPENFLIGHT_GATE11_SCREENSHOT, shot.toPNG());
    writeFileSync(resultPath, JSON.stringify(result));
  } catch (error) {
    writeFileSync(resultPath, JSON.stringify({ ok: false, error: String(error) }));
  } finally {
    app.quit();
  }
}

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
  if (process.env.OPENFLIGHT_GATE11_SMOKE === '1') {
    win.webContents.once('did-finish-load', () => void runDashboardSmoke(win));
  }
  if (app.isPackaged || process.env.OPENFLIGHT_PORTABLE === '1' || (!process.defaultApp && existsSync(fileURLToPath(new URL('../dist/index.html', import.meta.url))))) {
    // The portable Windows bundle starts its bundled UI without a terminal or server.
    // Hardware/backend features remain unavailable until a supported service is connected.
    win.loadFile(fileURLToPath(new URL('../dist/index.html', import.meta.url)));
  } else {
    win.loadURL(targetUrl);
  }

  win.on('closed', () => {
    app.quit();
  });
}

app.whenReady().then(async () => {
  await launchOptInBackend();
  if (backendStartupError || (backendChild && !backendReady)) {
    console.error("Backend unavailable; UI opens without it");
  }
  createWindow();
});

app.on("before-quit", () => stopBackend(backendChild));

app.on('window-all-closed', () => {
  app.quit();
});
