/**
 * Windows development bootstrap for the existing OpenFlight server + Electron UI.
 * No camera or radar hardware is required. Not a packaged application.
 *
 * Prerequisites: Python with OpenFlight backend dependencies, Node/npm,
 * and 'npm ci' already run in ui/. The Python interpreter can be selected
 * with OPENFLIGHT_PYTHON. The launcher does not install dependencies.
 */
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const uiDir = path.join(root, 'ui');
const host = '127.0.0.1';
const port = Number(process.env.OPENFLIGHT_WEB_PORT ?? '8080');
const timeoutMs = Number(process.env.OPENFLIGHT_STARTUP_TIMEOUT_MS ?? '30000');
const python = process.env.OPENFLIGHT_PYTHON || 'python';
const url = `http://${host}:${port}`;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export function validateOptions(options) {
  if (!Number.isInteger(options.port) || options.port < 1 || options.port > 65535) {
    throw new Error('OPENFLIGHT_WEB_PORT must be an integer between 1 and 65535');
  }
  if (!Number.isFinite(options.timeoutMs) || options.timeoutMs <= 0) {
    throw new Error('OPENFLIGHT_STARTUP_TIMEOUT_MS must be positive');
  }
}

export async function waitForHttpReady(target, timeout, child, request = fetch) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    if (child.spawnError) throw new Error(`OpenFlight backend failed to start: ${child.spawnError.message}`);
    if (child.exitCode !== null || child.signalCode !== null) {
      throw new Error('OpenFlight backend exited before becoming ready');
    }
    try {
      const response = await request(target, { signal: AbortSignal.timeout(1000) });
      if (response.ok) return;
    } catch {
      // The backend has not started listening yet.
    }
    await sleep(200);
  }
  throw new Error(`OpenFlight backend did not become ready within ${timeout}ms`);
}

export async function stopProcess(child) {
  if (!child || child.exitCode !== null || child.signalCode !== null) return;
  if (process.platform === 'win32') {
    if (!child.pid) return;
    // npm.cmd may spawn a process tree. Stop its descendants too.
    await new Promise((resolve) => {
      const killer = spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'], {
        stdio: 'ignore', windowsHide: true,
      });
      killer.on('error', resolve);
      killer.on('close', resolve);
    });
  } else {
    child.kill('SIGTERM');
    await Promise.race([
      new Promise((resolve) => child.once('exit', resolve)),
      sleep(2000),
    ]);
    if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
  }
}

export async function main() {
  validateOptions({ port, timeoutMs });
  if (!existsSync(path.join(uiDir, 'node_modules'))) {
    throw new Error('Electron dependencies missing. Run: cd ui && npm ci');
  }
  const environment = {
    ...process.env,
    PYTHONPATH: [path.join(root, 'src'), process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
    OPENFLIGHT_URL: url,
  };
  const backend = spawn(python, [
    '-m', 'openflight.server', '--mock', '--host', host, '--web-port', String(port),
  ], { cwd: root, env: environment, stdio: 'inherit', windowsHide: true });
  backend.on('error', (error) => { backend.spawnError = error; });
  let electron;
  let stopping = false;
  const shutdown = async () => {
    if (stopping) return;
    stopping = true;
    await stopProcess(electron);
    await stopProcess(backend);
  };
  const onSignal = () => { void shutdown(); };
  process.once('SIGINT', onSignal);
  process.once('SIGTERM', onSignal);
  try {
    await waitForHttpReady(url, timeoutMs, backend);
    if (stopping) return;
    const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    electron = spawn(npm, ['run', 'electron'], {
      cwd: uiDir, env: environment, stdio: 'inherit',
      shell: process.platform === 'win32', windowsHide: true,
    });
    await new Promise((resolve, reject) => {
      electron.once('error', reject);
      electron.once('exit', (code, signal) => {
        if (code === 0 || stopping || signal === 'SIGTERM') resolve();
        else reject(new Error(`Electron exited with code ${code ?? signal}`));
      });
    });
  } finally {
    process.removeListener('SIGINT', onSignal);
    process.removeListener('SIGTERM', onSignal);
    await shutdown();
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error('[OpenFlight Windows bootstrap]', error.message);
    process.exitCode = 1;
  });
}
