import assert from 'node:assert/strict';
import { test } from 'node:test';
import { resolveBackendExecutable, stopBackend } from './backendProcess.js';

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
