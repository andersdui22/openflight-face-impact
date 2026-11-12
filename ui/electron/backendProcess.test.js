import assert from 'node:assert/strict';
import { test } from 'node:test';
import { resolveBackendExecutable, stopBackend, waitForBackendReady, probeBackendHealth } from './backendProcess.js';

test('backend disabled by default', () => {
  assert.equal(resolveBackendExecutable({}), null);
});
test('relative executable rejected without invoking a shell', () => {
  assert.throws(
    () => resolveBackendExecutable({ OPENFLIGHT_BACKEND_EXECUTABLE: 'python' }),
    /existing absolute path/,
  );
});
test('missing absolute executable rejected', () => {
  const path = process.platform === 'win32' ? 'C:\\not-real\\backend.exe' : '/not-real/backend';
  assert.throws(
    () => resolveBackendExecutable({ OPENFLIGHT_BACKEND_EXECUTABLE: path }),
    /existing absolute path/,
  );
});
test('shutdown is safe when no backend started', () => {
  assert.doesNotThrow(() => stopBackend(null));
});


test('readiness retries until backend is reachable', async () => {
  let calls = 0;
  const ready = await waitForBackendReady({
    probe: async () => ++calls === 3,
    attempts: 4,
    delayMs: 0,
  });
  assert.equal(ready, true);
  assert.equal(calls, 3);
});

test('readiness stops when backend child has exited', async () => {
  let calls = 0;
  const ready = await waitForBackendReady({
    probe: async () => { calls += 1; return false; },
    isRunning: () => calls === 0,
    attempts: 4,
    delayMs: 0,
  });
  assert.equal(ready, false);
  assert.equal(calls, 1);
});

test('health probe rejects non-loopback targets', async () => {
  await assert.rejects(
    probeBackendHealth({ host: 'example.com' }),
    /loopback host/,
  );
});
