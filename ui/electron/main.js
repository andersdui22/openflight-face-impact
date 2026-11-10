// Kiosk shell for the OpenFlight React UI. Loads whatever URL the launcher
// script gives it (the startup splash, then the app itself once it
// navigates there) in a chromeless, fullscreen window — this replaces
// scripts/start-kiosk.sh's old system-browser detection (chromium-browser /
// chromium / google-chrome / firefox) with one pinned Chromium version.

import { app, BrowserWindow, Menu } from 'electron';
import { fileURLToPath } from 'node:url';
import { existsSync } from 'node:fs';
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
  if (app.isPackaged || process.env.OPENFLIGHT_PORTABLE === '1' || existsSync(fileURLToPath(new URL('../dist/index.html', import.meta.url)))) {
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

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  app.quit();
});
