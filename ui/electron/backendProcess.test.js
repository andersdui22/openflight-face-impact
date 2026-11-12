import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createServer } from 'node:http';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
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


test('health probe rejects a different endpoint', async () => {
  await assert.rejects(
    probeBackendHealth({ path: '/other' }),
    /Unexpected backend health path/,
  );
});


async function withHealthServer(reply, callback) {
  const server = createServer((_req, response) => {
    response.writeHead(reply.status ?? 200, { 'content-type': 'application/json' });
    response.end(JSON.stringify(reply.body));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    return await callback(server.address().port);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test('health accepts matching Face Impact service identity', async () => {
  const valid = {
    service: 'openflight-face-impact', protocol_version: 1,
    status: 'ready', camera_validated: false,
  };
  await withHealthServer({ body: valid }, async (port) => {
    assert.equal(await probeBackendHealth({ port }), true);
  });
});

test('health rejects unrelated local HTTP server and incompatible protocol', async () => {
  for (const body of [
    { service: 'unrelated', protocol_version: 1, status: 'ready', camera_validated: false },
    { service: 'openflight-face-impact', protocol_version: 2, status: 'ready', camera_validated: false },
    { service: 'openflight-face-impact', protocol_version: 1, status: 'ready', camera_validated: true },
  ]) {
    await withHealthServer({ body }, async (port) => {
      assert.equal(await probeBackendHealth({ port }), false);
    });
  }
});

test('health rejects server error even with matching JSON', async () => {
  await withHealthServer({
    status: 503,
    body: {
      service: 'openflight-face-impact', protocol_version: 1,
      status: 'ready', camera_validated: false,
    },
  }, async (port) => {
    assert.equal(await probeBackendHealth({ port }), false);
  });
});


test('bundled backend is discovered only when executable exists', () => {
  const root = mkdtempSync(join(tmpdir(), 'face-impact-backend-'));
  try {
    assert.equal(resolveBackendExecutable({}, root), null);
    const directory = join(root, 'backend');
    mkdirSync(directory);
    const executable = join(directory, 'OpenFlightFaceImpactBackend.exe');
    writeFileSync(executable, '');
    assert.equal(resolveBackendExecutable({}, root), executable);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('explicit backend executable overrides bundled candidate', () => {
  const root = mkdtempSync(join(tmpdir(), 'face-impact-backend-'));
  try {
    const directory = join(root, 'backend');
    mkdirSync(directory);
    writeFileSync(join(directory, 'OpenFlightFaceImpactBackend.exe'), '');
    const explicit = join(root, 'explicit.exe');
    writeFileSync(explicit, '');
    assert.equal(resolveBackendExecutable({
      OPENFLIGHT_BACKEND_EXECUTABLE: explicit,
    }, root), explicit);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
