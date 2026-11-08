import test from 'node:test';
import assert from 'node:assert/strict';
import { validateOptions, usbCameraArgs, waitForHttpReady } from '../scripts/windows-bootstrap.mjs';

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

test('stopProcess terminates a live child process', async () => {
  const { spawn } = await import('node:child_process');
  const { once } = await import('node:events');
  const { stopProcess } = await import('../scripts/windows-bootstrap.mjs');
  const child = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], {
    stdio: 'ignore', windowsHide: true,
  });
  try {
    await Promise.race([
      once(child, 'spawn'),
      once(child, 'error').then(([error]) => { throw error; }),
    ]);
    assert.ok(child.pid, 'test child must have a PID');
    await stopProcess(child);
    if (child.exitCode === null && child.signalCode === null) {
      await Promise.race([
        once(child, 'exit'),
        new Promise((_, reject) => setTimeout(() => reject(new Error('child not terminated')), 5000)),
      ]);
    }
    assert.ok(child.exitCode !== null || child.signalCode !== null,
      'stopProcess must terminate its child');
  } finally {
    if (child.exitCode === null && child.signalCode === null) child.kill();
  }
});

test('USB camera is disabled by default and only enabled for a valid index', () => {
  assert.deepEqual(usbCameraArgs(undefined), []);
  assert.deepEqual(usbCameraArgs(''), []);
  assert.deepEqual(usbCameraArgs('0'), ['--windows-usb-camera', '0']);
  assert.deepEqual(usbCameraArgs('2'), ['--windows-usb-camera', '2']);
  for (const value of ['-1', '1.5', 'abc', '01', '999999999999999999999']) {
    assert.throws(() => usbCameraArgs(value), /OPENFLIGHT_USB_CAMERA_INDEX/);
  }
});
