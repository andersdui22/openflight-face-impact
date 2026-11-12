import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { resolveTargetUrl, DEFAULT_URL } from './resolveTargetUrl.js';

describe('resolveTargetUrl', () => {
  it('defaults to the local Flask server when nothing else is set', () => {
    assert.equal(resolveTargetUrl({}, ['electron', 'main.js']), DEFAULT_URL);
  });

  it('prefers OPENFLIGHT_URL over the CLI argument', () => {
    assert.equal(
      resolveTargetUrl({ OPENFLIGHT_URL: 'http://pi.local:8080' }, [
        'electron', 'main.js', 'http://cli-arg:8080',
      ]),
      'http://pi.local:8080',
    );
  });

  it('falls back to a CLI argument when the env var is unset', () => {
    assert.equal(
      resolveTargetUrl({}, ['electron', 'main.js', 'http://cli-arg:8080']),
      'http://cli-arg:8080',
    );
  });

  it('ignores an empty OPENFLIGHT_URL rather than passing it through', () => {
    assert.equal(
      resolveTargetUrl({ OPENFLIGHT_URL: '' }, ['electron', 'main.js', 'http://cli-arg:8080']),
      'http://cli-arg:8080',
    );
  });
});
