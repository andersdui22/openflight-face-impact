import { afterEach, expect, test, vi } from 'vitest';
import { getServerOrigin } from './serverOrigin';

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

test.each([
  ['file:///C:/OpenFlight/resources/app/dist/index.html', 'http://127.0.0.1:8080'],
  ['http://localhost:5173/', 'http://localhost:8080'],
  ['http://openflight.local:8081/display', 'http://openflight.local:8081'],
])('resolves the backend origin for %s', (url, expected) => {
  vi.stubEnv('VITE_SOCKET_URL', '');
  vi.stubGlobal('window', { location: new URL(url) });

  expect(getServerOrigin()).toBe(expected);
});

test('honors an explicit backend origin in the packaged renderer', () => {
  vi.stubGlobal('window', { location: new URL('file:///C:/OpenFlight/index.html') });
  vi.stubEnv('VITE_SOCKET_URL', 'http://localhost:9000');

  expect(getServerOrigin()).toBe('http://localhost:9000');
});
