import { randomUUID } from 'node:crypto';
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

const cameraToken = randomUUID();
let backendChild = null;
let backendStartupError = null;
let backendReady = false;
let quitting = false;
let backendStopped = false;
let smokeResult = null;
let backendRestartTimer = null;
let backendRestartsRemaining = 3;
let backendRecoveryEnabled = true;

function scheduleBackendRecovery() {
  if (quitting || !backendRecoveryEnabled || backendRestartTimer || backendRestartsRemaining === 0) return;
  backendRestartTimer = setTimeout(async () => {
    backendRestartTimer = null;
    if (quitting) return;
    backendRestartsRemaining -= 1;
    await launchOptInBackend(true);
    if (!backendReady && !quitting) {
      try {
        const shutdown = await stopBackend(backendChild);
        if (shutdown !== 'timeout') scheduleBackendRecovery();
      } catch (error) {
        console.error('Could not clean up failed backend recovery', error);
      }
    }
  }, 1500);
}

async function launchOptInBackend(recovering = false) {
  backendReady = false;
  backendStartupError = null;
  try {
    const executable = resolveBackendExecutable(process.env, app.isPackaged ? process.resourcesPath : null);
    backendChild = startBackend(executable, {
      cameraToken,
      onError: (error) => { backendStartupError = error; console.error(error); },
    });
    const child = backendChild;
    if (child) {
      child.once('exit', () => {
        if (backendChild !== child) return;
        const wasReady = backendReady;
        backendReady = false;
        // Failed recovery attempts are handled after their readiness probe settles.
        if (wasReady) scheduleBackendRecovery();
      });
      backendReady = await waitForBackendReady({
        probe: () => probeBackendHealth({ instance: child.openFlightInstance }),
        isRunning: () => !!child.pid && child.exitCode === null &&
          child.signalCode === null && !backendStartupError && !quitting,
      });
      if (!backendReady && !recovering) console.error("Face Impact backend readiness check failed");
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

async function verifyPackagedRecordingImport(win) {
  return win.webContents.executeJavaScript(`
    (async () => {
      const api = 'http://127.0.0.1:8080/api/face-impact/recordings';
      const headers = { 'X-OpenFlight-Recording': '1', 'Content-Type': 'application/json' };
      const response = await fetch(api + '/fixtures', { method: 'POST', headers, body: '{"case":"contact"}' });
      if (!response.ok) throw new Error('Packaged recording receipt creation failed');
      const { digest } = await response.json();
      const zip = await fetch(api + '/' + digest, { headers });
      if (!zip.ok) throw new Error('Packaged sample ZIP unavailable');
      const panel = document.querySelector('[aria-label="Recorded synthetic captures"]');
      panel.querySelector('summary').click();
      const findButton = (label) => [...panel.querySelectorAll('button')].find((item) => item.textContent.trim() === label);
      const wait = async (predicate, message) => {
        for (let attempt = 0; attempt < 100; attempt++) {
          if (predicate()) return;
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
        throw new Error(message + ': ' + (panel.querySelector('[role="alert"]')?.textContent || 'timeout'));
      };
      const input = panel.querySelector('input[type="file"]');
      await wait(() => !input.disabled, 'Recording picker unavailable');
      const files = new DataTransfer();
      files.items.add(new File([await zip.blob()], 'fixture.zip', { type: 'application/zip' }));
      input.files = files.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      await wait(() => !findButton('Import recording').disabled, 'Import action unavailable');
      findButton('Import recording').click();
      await wait(() => panel.textContent.includes('Independent synthetic receipt matched'), 'Receipt did not match');
      findButton('Replay recording').click();
      await wait(() => panel.textContent.includes('Synthetic replay accepted and saved'), 'Replay did not save');
      panel.scrollIntoView({ block: 'start' });
      await new Promise(requestAnimationFrame);
      return digest;
    })()
  `);
}

async function runDashboardSmoke(win) {
  const expectsBackend = process.env.OPENFLIGHT_GATE11_EXPECT_BACKEND === '1';
  const expectsSavedSession = process.env.OPENFLIGHT_GATE11_EXPECT_SAVED_SESSION === '1';
  const expectsRejectedShot = process.env.OPENFLIGHT_GATE11_EXPECT_REJECTED_SHOT === '1';
  const closeMode = process.env.OPENFLIGHT_GATE11_CLOSE_MODE ?? 'internal';
  const resultPath = process.env.OPENFLIGHT_GATE11_RESULT;
  const usbFixture = process.env.OPENFLIGHT_GATE11_USB_FIXTURE === '1';
  try {
    if (backendReady !== expectsBackend) {
      throw new Error(`Expected mock backend ready=${expectsBackend}, got ${backendReady}`);
    }
    const result = await win.webContents.executeJavaScript(`
      (async (expectsBackend, expectsSavedSession, expectsRejectedShot, usbFixture) => {
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
        let cameraStatus = expectsBackend ? 'Camera: disabled' : 'Camera: offline';
        if (usbFixture) {
          const control = async (action) => {
            const response = await fetch('http://127.0.0.1:8080/api/test/usb-camera/' + action, {
              method: 'POST',
              headers: { 'X-OpenFlight-Smoke': 'usb-fixture' },
            });
            if (!response.ok) throw new Error('USB fixture action failed: ' + action);
            return response.json();
          };
          const width = () => preview.querySelector('img')?.naturalWidth;
          await waitFor(() => width() === 96, 'Expected delivered USB fixture preview at 96 pixels');
          const capture = await control('trigger');
          if (JSON.stringify(capture.frame_sizes) !== '[[96,64],[96,64]]' ||
              !capture.host_clock_aliases.every(Boolean) ||
              capture.rejection !== 'independent sensor timestamp unavailable') {
            throw new Error('USB trigger lost raster or timing provenance');
          }
          await control('disconnect');
          await waitFor(() => !width() && preview.textContent.includes('disconnected'),
            'USB fixture disconnect did not clear preview');
          if (!(await control('restart')).previous_handle_released) {
            throw new Error('USB fixture reopened without releasing the old handle');
          }
          await waitFor(() => width() === 80 && !preview.querySelector('[role="alert"]'),
            'USB fixture recovery did not deliver the new raster');
          if (!preview.textContent.includes('Calibration profile incompatible with camera mode') ||
              !dashboard.textContent.includes('No measured impacts yet')) {
            throw new Error('USB fixture did not report incompatible calibration without measurements');
          }
          cameraStatus = 'Camera: recovered USB fixture';
          const recovered = await control('trigger');
          if (JSON.stringify(recovered.frame_sizes) !== '[[80,48],[80,48]]') {
            throw new Error('USB fixture recovery retained a stale raster');
          }
        } else {
          await waitFor(() => preview?.textContent.includes(cameraStatus), 'Expected ' + cameraStatus);
        }
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
        return { ok: true, panels: panels.length, backend_ready: expectsBackend, usb_fixture: usbFixture,
          camera: cameraStatus, restored_session: expectsSavedSession };
      })(${JSON.stringify(expectsBackend)}, ${JSON.stringify(expectsSavedSession)}, ${JSON.stringify(expectsRejectedShot)}, ${JSON.stringify(usbFixture)})
    `);
    if (expectsSavedSession) {
      await verifySessionDownload(win, join(dirname(resultPath), 'exported-session-' + basename(resultPath)), expectsRejectedShot);
    }
    result.exported_session = expectsSavedSession;
    result.reconnected = expectsBackend && !expectsSavedSession;
    if (result.reconnected) await verifyRendererReconnect(win);
    if (expectsRejectedShot) {
      const digest = await verifyPackagedRecordingImport(win);
      await verifyRendererReconnect(win);
      result.recording_import = await win.webContents.executeJavaScript(`
        (async () => {
          const response = await fetch('http://127.0.0.1:8080/api/face-impact/recordings', {
            headers: { 'X-OpenFlight-Recording': '1' },
          });
          if (!response.ok) return false;
          const { recordings } = await response.json();
          return recordings.some((item) => item.zip_sha === ${JSON.stringify(digest)});
        })()
      `);
      if (!result.recording_import) throw new Error('Imported recording was lost after backend restart');
    }
    if (expectsBackend && !expectsSavedSession && !usbFixture) {
      await win.webContents.executeJavaScript(`
        (async () => {
          const endpoint = 'http://127.0.0.1:8080/api/face-impact/camera-setup/';
          const call = (action, body) => fetch(endpoint + action, {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-OpenFlight-Camera-Setup': '1' },
            body: JSON.stringify(body),
          });
          const inventory = await call('inventory', {});
          if (!inventory.ok || !Array.isArray((await inventory.json()).devices)) {
            throw new Error('Packaged Windows PnP inventory unavailable');
          }
          const setup = document.querySelector('[aria-label="Face Impact camera setup"]');
          setup.querySelector('summary').click();
          const start = [...setup.querySelectorAll('button')].find(button => button.textContent.trim() === 'Start or reconnect fixture');
          start.click();
          for (let attempt = 0; attempt < 100; attempt++) {
            if (setup.textContent.includes('320 × 200') && setup.textContent.includes('fixture · fixture_match')) {
              const status = await (await fetch('http://127.0.0.1:8080/api/camera/usb/status')).json();
              if (status.capture_diagnostics?.buffer.history_frames < 18) {
                await new Promise(resolve => setTimeout(resolve, 100));
                continue;
              }
              const response = await call('record', { pre_frames: 18, post_frames: 20 });
              if (!response.ok || response.headers.get('X-OpenFlight-Exported-Frames') !== '38' ||
                  (await response.blob()).size < 1000) {
                throw new Error('Packaged 38-frame diagnostic ZIP unavailable');
              }
              const stopped = await call('stop', {});
              if (!stopped.ok) throw new Error('Packaged fixture did not stop');
              return;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
          }
          throw new Error('Packaged camera setup did not deliver fixture frames');
        })()
      `);
    }
    const shot = await win.webContents.capturePage();
    const { width, height } = shot.getSize();
    if (width < 800 || height < 400) {
      throw new Error(`Dashboard capture has invalid dimensions ${width}x${height}`);
    }
    writeFileSync(process.env.OPENFLIGHT_GATE11_SCREENSHOT, shot.toPNG());
    if (closeMode === 'backend-loss') {
      await replayBeforeBackendLoss(win);
      // This scenario exercises exit while the owned backend is already down.
      backendRecoveryEnabled = false;
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
  const crashed = backendChild;
  const disconnected = expectConnection('Synthetic replay requires a backend connection');
  crashed.kill('SIGKILL');
  await disconnected;
  await expectConnection('Python backend connected for replay');
  // The renderer can reconnect before Electron's next independent health probe.
  const newBackendReady = await waitForBackendReady({
    probe: async () => backendReady && backendChild !== crashed &&
      backendChild.openFlightInstance !== crashed.openFlightInstance,
    isRunning: () => !quitting,
    attempts: 30,
    delayMs: 100,
  });
  if (!newBackendReady) throw new Error('Owned backend did not recover with a new process identity');
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

  if (portable) {
    win.webContents.session.webRequest.onBeforeSendHeaders(
      { urls: ['http://127.0.0.1:8080/api/face-impact/camera-setup/*', 'http://127.0.0.1:8080/api/camera/preview.jpg*'] },
      (details, callback) => {
        if (details.webContentsId === win.webContents.id && win.webContents.getURL() === portableIndex.href) {
          details.requestHeaders['X-OpenFlight-Physical-Camera'] = cameraToken;
        }
        callback({ requestHeaders: details.requestHeaders });
      },
    );
  }
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
  if (backendStopped) return;
  if (backendChild) event.preventDefault();
  if (quitting) return;
  quitting = true;
  clearTimeout(backendRestartTimer);
  if (!backendChild) return;
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
