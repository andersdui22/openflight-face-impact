// Kiosk shell for the OpenFlight React UI. Loads whatever URL the launcher
// script gives it (the startup splash, then the app itself once it
// navigates there) in a chromeless, fullscreen window — this replaces
// scripts/start-kiosk.sh's old system-browser detection (chromium-browser /
// chromium / google-chrome / firefox) with one pinned Chromium version.

import { app, BrowserWindow, ipcMain, Menu } from 'electron';
import { fileURLToPath } from 'node:url';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { resolveTargetUrl } from './resolveTargetUrl.js';
import { probeBackendHealth, resolveBackendExecutable, startBackend, stopBackend, waitForBackendReady } from './backendProcess.js';

const targetUrl = resolveTargetUrl(process.env, process.argv);
const portableIndex = new URL('../dist/index.html', import.meta.url);
const portable = app.isPackaged || process.env.OPENFLIGHT_PORTABLE === '1' ||
  (!process.defaultApp && existsSync(fileURLToPath(portableIndex)));

Menu.setApplicationMenu(null);

let backendChild = null;
let backendStartupError = null;
let backendReady = false;
let quitting = false;
let backendStopped = false;
let smokeResult = null;

async function launchOptInBackend() {
  try {
    const executable = resolveBackendExecutable(process.env, app.isPackaged ? process.resourcesPath : null);
    backendChild = startBackend(executable, {
      onError: (error) => { backendStartupError = error; console.error(error); },
    });
    if (backendChild) {
      backendReady = await waitForBackendReady({
        probe: () => probeBackendHealth({ instance: backendChild.openFlightInstance }),
        isRunning: () => !!backendChild.pid && backendChild.exitCode === null &&
          backendChild.signalCode === null && !backendStartupError && !quitting,
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
async function verifySessionDownload(win, path, expectsRejectedShot) {
  const session = win.webContents.session;
  let onDownload;
  let timer;
  const downloaded = new Promise((resolve, reject) => {
    timer = setTimeout(() => reject(new Error('Session export did not complete')), 10000);
    onDownload = (_event, item) => {
      item.setSavePath(path);
      item.once('done', (_doneEvent, state) => {
        if (state === 'completed') resolve();
        else reject(new Error(`Session export ended with ${state}`));
      });
    };
    session.once('will-download', onDownload);
  });
  try {
    await Promise.all([downloaded, win.webContents.executeJavaScript(`
      document.querySelector('[aria-label="Offline synthetic impact review"] a[href$="?download=1"]').click()
    `)]);
  } finally {
    clearTimeout(timer);
    session.removeListener('will-download', onDownload);
  }
  const exported = JSON.parse(readFileSync(path, 'utf8'));
  if (exported.source !== 'offline_synthetic_analysis' ||
      exported.shots.filter(({ evidence, provenance }) =>
        evidence.shot_id.startsWith('synthetic-contact-') && evidence.accepted &&
        provenance.capture.acquisition === 'synthetic-triggered-ring-v1').length !== 2 ||
      (expectsRejectedShot && !exported.shots.some(({ evidence }) =>
        evidence.shot_id.startsWith('synthetic-missing-ball-') && !evidence.accepted)) ||
      !exported.analysis.clubs.some((club) => club.points_mm.length === 2 && club.mean_mm.length === 2 &&
        club.spread_mm?.every((axis) => axis === 0))) {
    throw new Error('Downloaded session lacks the archived shot and statistics');
  }
}

async function runDashboardSmoke(win) {
  const expectsBackend = process.env.OPENFLIGHT_GATE11_EXPECT_BACKEND === '1';
  const expectsSavedSession = process.env.OPENFLIGHT_GATE11_EXPECT_SAVED_SESSION === '1';
  const expectsRejectedShot = process.env.OPENFLIGHT_GATE11_EXPECT_REJECTED_SHOT === '1';
  const closeMode = process.env.OPENFLIGHT_GATE11_CLOSE_MODE ?? 'internal';
  const resultPath = process.env.OPENFLIGHT_GATE11_RESULT;
  try {
    if (backendReady !== expectsBackend) {
      throw new Error(`Expected mock backend ready=${expectsBackend}, got ${backendReady}`);
    }
    const result = await win.webContents.executeJavaScript(`
      (async (expectsBackend, expectsSavedSession, expectsRejectedShot) => {
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
          const button = (label) => Array.from(review?.querySelectorAll('button') ?? [])
            .find((item) => item.textContent === label);
          if (expectsSavedSession) {
            review.querySelector('details').open = true;
            const load = await waitFor(() => {
              const item = button('Load session');
              return item && !item.disabled && item;
            }, 'Saved synthetic session did not survive backend restart');
            load.click();
          } else {
            const replay = button('Run synthetic replay');
            if (!replay) throw new Error('Offline replay button not rendered');
            replay.click();
            await waitFor(() => !replay.disabled &&
              review.textContent.includes('Saved shots 1 · Accepted 1 · Rejected 0'),
              'First replay did not update the saved analysis');
            replay.click();
          }
          if (expectsRejectedShot) {
            await waitFor(() => review.textContent.includes('REJECTED:'),
              'Rejected evidence did not survive backend loss');
            if (review.querySelector('[data-testid="synthetic-impact-marker"]')) {
              throw new Error('Restored rejected evidence displayed an impact marker');
            }
            Array.from(review.querySelectorAll('button'))
              .find((item) => item.textContent.includes('synthetic-contact'))?.click();
          }
          await waitFor(() => review.textContent.includes(
            expectsSavedSession ? 'Loaded from saved session' : 'Received from Python replay') &&
            review.textContent.includes('Selected shot: synthetic-contact') &&
            review.querySelector('[data-testid="synthetic-impact-marker"]'),
            'Mock backend did not deliver offline raster evidence');
          const analysis = await waitFor(() => {
            const section = review.querySelector('[aria-label="Saved synthetic session analysis"]');
            const summary = expectsRejectedShot
              ? 'Saved shots 3 · Accepted 2 · Rejected 1'
              : 'Saved shots 2 · Accepted 2 · Rejected 0';
            return section?.textContent.includes(summary) &&
              section.textContent.includes('Spread (standard deviation) X 0.00 mm · Y 0.00 mm') && section;
          }, 'Repeated shots and their statistics did not render');
          if (!expectsSavedSession) {
            const replay = button('Run synthetic replay');
            const select = review.querySelector('select');
            for (const [fixture, reason] of [
              ['invalid-frame', 'Synthetic capture rejected'],
              ['missing-markers', 'Synthetic marker or geometry analysis rejected'],
            ]) {
              select.value = fixture;
              select.dispatchEvent(new Event('change', { bubbles: true }));
              await new Promise((resolve) => requestAnimationFrame(resolve));
              replay.click();
              await waitFor(() => review.querySelector('[role="alert"]')?.textContent === reason,
                'Packaged backend did not reject ' + fixture);
              if (!review.textContent.includes('OFFLINE RESULTS: 2 · SYNTHETIC ACCEPTED: 2')) {
                throw new Error('Rejected capture changed the saved shot count');
              }
            }
          }
          analysis.querySelector('details').open = true;
          analysis.scrollIntoView({ block: 'start' });
        } else {
          await waitFor(() => dashboard.textContent.includes('OpenFlight backend is disconnected'),
            'UI did not report the disconnected backend');
          if (marker()) throw new Error('Disconnected dashboard displayed a synthetic marker');
        }
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        return { ok: true, panels: panels.length, backend_ready: expectsBackend,
          camera: cameraStatus, restored_session: expectsSavedSession };
      })(${JSON.stringify(expectsBackend)}, ${JSON.stringify(expectsSavedSession)}, ${JSON.stringify(expectsRejectedShot)})
    `);
    if (expectsSavedSession) {
      await verifySessionDownload(win, join(dirname(resultPath), 'exported-session-' + basename(resultPath)), expectsRejectedShot);
    }
    result.exported_session = expectsSavedSession;
    result.reconnected = expectsBackend && !expectsSavedSession;
    if (result.reconnected) await verifyRendererReconnect(win);
    const shot = await win.webContents.capturePage();
    const { width, height } = shot.getSize();
    if (width < 800 || height < 400) {
      throw new Error(`Dashboard capture has invalid dimensions ${width}x${height}`);
    }
    writeFileSync(process.env.OPENFLIGHT_GATE11_SCREENSHOT, shot.toPNG());
    if (closeMode === 'backend-loss') {
      await replayBeforeBackendLoss(win);
      backendChild.kill('SIGKILL');
      await waitForRendererDisconnect(win);
    }
    smokeResult = { ...result, close_mode: closeMode, restored_rejection: expectsRejectedShot };
    writeFileSync(resultPath, JSON.stringify(smokeResult));
    if (closeMode === 'window') {
      win.close();
    } else {
      await win.webContents.executeJavaScript(`
        (async () => {
          document.querySelector('.panel-footer__power').click();
          for (let attempt = 0; attempt < 100; attempt++) {
            const confirm = document.querySelector('.shutdown-dialog__confirm');
            if (confirm) {
              confirm.click();
              return;
            }
            await new Promise((resolve) => setTimeout(resolve, 100));
          }
          throw new Error('In-app shutdown confirmation did not render');
        })()
      `);
    }
  } catch (error) {
    // IPC can destroy the renderer while its confirmation script returns.
    if (smokeResult && (quitting || win.isDestroyed())) return;
    smokeResult = null;
    writeFileSync(resultPath, JSON.stringify({ ok: false, error: String(error) }));
    app.quit();
  }
}

async function verifyRendererReconnect(win) {
  const expectConnection = (message) => win.webContents.executeJavaScript(`
    (async () => {
      const status = document.querySelector('[aria-label="Replay connection"]');
      for (let attempt = 0; attempt < 150; attempt++) {
        if (status.textContent === ${JSON.stringify(message)}) return;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      throw new Error('Expected Socket.IO state: ' + ${JSON.stringify(message)});
    })()
  `);
  if (await stopBackend(backendChild) !== 'graceful') {
    throw new Error('Owned backend did not exit gracefully before restart');
  }
  await expectConnection('Synthetic replay requires a backend connection');
  await launchOptInBackend();
  if (!backendReady) throw new Error('Owned backend did not restart');
  await expectConnection('Python backend connected for replay');
}

function replayBeforeBackendLoss(win) {
  return win.webContents.executeJavaScript(`
    (async () => {
      const review = document.querySelector('[aria-label="Offline synthetic impact review"]');
      const select = review.querySelector('select');
      select.value = 'missing-ball';
      select.dispatchEvent(new Event('change', { bubbles: true }));
      const replay = Array.from(review.querySelectorAll('button'))
        .find((button) => button.textContent === 'Run synthetic replay');
      replay.click();
      for (let attempt = 0; attempt < 100; attempt++) {
        if (review.textContent.includes('Selected shot: synthetic-missing-ball') &&
            review.textContent.includes('REJECTED:') && !replay.disabled) return;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      throw new Error('Rejected replay was not committed before backend loss');
    })()
  `);
}

function waitForRendererDisconnect(win) {
  return win.webContents.executeJavaScript(`
    (async () => {
      const review = document.querySelector('[aria-label="Offline synthetic impact review"]');
      for (let attempt = 0; attempt < 100; attempt++) {
        if (review.querySelector('[aria-label="Replay connection"]').textContent.includes('requires a backend connection') &&
            review.textContent.includes('OFFLINE RESULTS: 3 · SYNTHETIC ACCEPTED: 2')) return;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      throw new Error('Backend loss did not update the connection status while retaining replay evidence');
    })()
  `);
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
      ...(portable && {
        preload: fileURLToPath(new URL('./desktopPreload.cjs', import.meta.url)),
        additionalArguments: !backendReady && (backendChild || backendStartupError)
          ? ['--openflight-backend-unavailable'] : [],
      }),
    },
  });

  win.setMenuBarVisibility(false);
  // The kiosk shell only ever shows the OpenFlight UI itself; deny any
  // attempt (e.g. target="_blank" links) to pop a second window.
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  if (process.env.OPENFLIGHT_GATE11_SMOKE === '1') {
    win.webContents.once('did-finish-load', () => void runDashboardSmoke(win));
  }
  if (portable) {
    const quitFromRenderer = (event) => {
      if (event.sender === win.webContents && event.senderFrame === win.webContents.mainFrame &&
          event.senderFrame?.url === portableIndex.href) app.quit();
    };
    ipcMain.on('openflight:quit', quitFromRenderer);
    win.once('closed', () => ipcMain.removeListener('openflight:quit', quitFromRenderer));
    win.loadFile(fileURLToPath(portableIndex));
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
  if (!quitting) createWindow();
});

app.on('before-quit', (event) => {
  if (backendStopped || !backendChild) return;
  event.preventDefault();
  if (quitting) return;
  quitting = true;
  void stopBackend(backendChild).then((outcome) => {
    backendStopped = true;
    if (smokeResult) {
      writeFileSync(process.env.OPENFLIGHT_GATE11_RESULT, JSON.stringify({
        ...smokeResult, backend_shutdown: outcome, backend_pid: backendChild.pid,
      }));
    }
    if (outcome === 'timeout') app.exit(1);
    else app.quit();
  }).catch((error) => {
    console.error('Could not stop the owned OpenFlight backend', error);
    app.exit(1);
  });
});

app.on('window-all-closed', () => {
  app.quit();
});
