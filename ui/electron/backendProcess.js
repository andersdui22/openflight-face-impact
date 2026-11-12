// Opt-in Windows backend lifecycle. Never spawn an implicit shell command.
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { isAbsolute, join } from 'node:path';
import { request } from 'node:http';

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
  const child = spawn(executable, ['--mock', '--host', '127.0.0.1',
    '--web-port', '8080', '--no-logging'], {
    cwd: options.cwd,
    windowsHide: true,
    shell: false,
    stdio: 'ignore',
  });
  child.on('error', (error) => {
    options.onError?.(error);
  });
  return child;
}

export function stopBackend(child) {
  if (child && child.exitCode === null && !child.killed) {
    child.kill();
  }
}


export function probeBackendHealth({
  host = '127.0.0.1', port = 8080,
  path = '/api/face-impact/health', timeoutMs = 1000,
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
            data.camera_validated === false);
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
    if (await probe()) return true;
    if (attempt + 1 < attempts) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  return false;
}
