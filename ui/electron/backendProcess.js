// Opt-in Windows backend lifecycle. Never spawn an implicit shell command.
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { isAbsolute, join } from 'node:path';
import { request } from 'node:http';
import { randomUUID } from 'node:crypto';

export function resolveBackendExecutable(env = process.env, resourcesPath = null) {
  const explicit = env.OPENFLIGHT_BACKEND_EXECUTABLE;
  const bundled = resourcesPath ? join(resourcesPath, 'backend', 'OpenFlightFaceImpactBackend.exe') : null;
  const candidate = explicit || (bundled && existsSync(bundled) ? bundled : null);
  if (!candidate) return null;
  if (!isAbsolute(candidate) || !existsSync(candidate)) {
    throw new Error('Backend executable must be an existing absolute path');
  }
  return candidate;
}

export function startBackend(executable, options = {}) {
  if (!executable) return null;
  const instance = randomUUID();
  const child = spawn(executable, ['--mock', '--host', '127.0.0.1',
    '--web-port', '8080', '--no-logging'], {
    cwd: options.cwd,
    windowsHide: true,
    shell: false,
    env: { ...process.env, OPENFLIGHT_DESKTOP_INSTANCE: instance },
    stdio: ['pipe', 'ignore', 'ignore'],
  });
  child.openFlightInstance = instance;
  // The pipe can close when a child exits during startup.
  child.stdin.on('error', () => {});
  child.on('error', (error) => {
    options.onError?.(error);
  });
  return child;
}

function hasExited(child) {
  return !child?.pid || child.exitCode !== null || child.signalCode !== null;
}

function waitForExit(child, timeoutMs) {
  if (hasExited(child)) return Promise.resolve(true);
  return new Promise((resolve) => {
    const finish = (exited) => {
      clearTimeout(timer);
      child.removeListener('exit', onExit);
      resolve(exited);
    };
    const onExit = () => finish(true);
    const timer = setTimeout(() => finish(false), timeoutMs);
    child.once('exit', onExit);
  });
}

export async function stopBackend(child, { graceMs = 4500, forceMs = 2500 } = {}) {
  if (hasExited(child)) return 'already-exited';
  const gracefulExit = waitForExit(child, graceMs);
  child.stdin?.end();
  if (await gracefulExit) return 'graceful';
  const forcedExit = waitForExit(child, forceMs);
  if (!hasExited(child)) child.kill('SIGKILL');
  return (await forcedExit) ? 'forced' : 'timeout';
}


export function probeBackendHealth({
  host = '127.0.0.1', port = 8080,
  path = '/api/face-impact/health', timeoutMs = 1000, instance,
} = {}) {
  if (host !== '127.0.0.1' && host !== 'localhost') {
    return Promise.reject(new Error('Backend health probe requires loopback host'));
  }
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    return Promise.reject(new Error('Invalid backend port'));
  }
  if (path !== '/api/face-impact/health') {
    return Promise.reject(new Error('Unexpected backend health path'));
  }
  return new Promise((resolve) => {
    const req = request({ hostname: host, port, path, method: 'GET',
      timeout: timeoutMs }, (response) => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', (chunk) => {
        body += chunk;
        if (body.length > 4096) req.destroy();
      });
      response.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve(response.statusCode === 200 &&
            data.service === 'openflight-face-impact' &&
            data.protocol_version === 1 && data.status === 'ready' &&
            data.camera_validated === false && (instance === undefined || data.desktop_instance === instance));
        } catch {
          resolve(false);
        }
      });
    });
    req.on('timeout', () => req.destroy());
    req.on('error', () => resolve(false));
    req.end();
  });
}

export async function waitForBackendReady({
  probe = probeBackendHealth, attempts = 20, delayMs = 250,
  isRunning = () => true,
} = {}) {
  if (!Number.isInteger(attempts) || attempts < 1 || attempts > 120) {
    throw new Error('Invalid readiness attempt budget');
  }
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    if (!isRunning()) return false;
    if (await probe()) return isRunning();
    if (attempt + 1 < attempts) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  return false;
}
