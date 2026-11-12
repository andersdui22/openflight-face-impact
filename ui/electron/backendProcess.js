// Opt-in Windows backend lifecycle. Never spawn an implicit shell command.
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { isAbsolute } from 'node:path';

export function resolveBackendExecutable(env = process.env) {
  const candidate = env.OPENFLIGHT_BACKEND_EXECUTABLE;
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
