import test from 'node:test';
import assert from 'node:assert/strict';
import { validateOptions, waitForHttpReady } from '../scripts/windows-bootstrap.mjs';

test('validates port and startup timeout', () => {
  assert.doesNotThrow(() => validateOptions({ port: 8080, timeoutMs: 100 }));
  assert.throws(() => validateOptions({ port: 0, timeoutMs: 100 }), /WEB_PORT/);
  assert.throws(() => validateOptions({ port: 8080, timeoutMs: 0 }), /TIMEOUT/);
});

test('accepts an HTTP-ready backend', async () => {
  let calls = 0;
  const request = async () => {
    calls += 1;
    return { ok: true };
  };
  await waitForHttpReady('http://127.0.0.1:8080', 1000,
    { exitCode: null, signalCode: null }, request);
  assert.equal(calls, 1);
});

test('rejects a backend that already exited', async () => {
  await assert.rejects(
    waitForHttpReady('http://127.0.0.1:8080', 100,
      { exitCode: 1, signalCode: null }, async () => ({ ok: true })),
    /exited before becoming ready/,
  );
});

test('rejects a backend that never responds', async () => {
  await assert.rejects(
    waitForHttpReady('http://127.0.0.1:8080', 30,
      { exitCode: null, signalCode: null }, async () => { throw Error('offline'); }),
    /did not become ready/,
  );
});

test('reports an unavailable Python executable without waiting for timeout', async () => {
  await assert.rejects(
    waitForHttpReady('http://127.0.0.1:8080', 100,
      { exitCode: null, signalCode: null, spawnError: new Error('ENOENT') },
      async () => ({ ok: true })),
    /failed to start: ENOENT/,
  );
});
