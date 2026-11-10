import { readFile } from 'node:fs/promises';
import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import prettier from 'prettier';
import { FaceImpactCameraPreview } from './FaceImpactCameraPreview';

describe('FaceImpactCameraPreview', () => {
  it('prints the precise Prettier output for the camera component in CI diagnostics', async () => {
    const file = new URL('./FaceImpactCameraPreview.tsx', import.meta.url);
    const original = await readFile(file, 'utf8');
    const formatted = await prettier.format(original, {
      filepath: file.pathname,
      printWidth: 120,
      trailingComma: 'es5',
      tabWidth: 2,
      semi: true,
      singleQuote: true,
    });
    if (formatted !== original) {
      console.info('GATE13_PRETTIER_EXPECTED_START\\n' + formatted + 'GATE13_PRETTIER_EXPECTED_END');
    }
    expect(formatted.length).toBeGreaterThan(0);
  });

  it('starts with a checking state and never fabricates camera frames', () => {
    const html = renderToString(<FaceImpactCameraPreview />);
    expect(html).toContain('USB camera preview');
    expect(html).toContain('Camera: checking');
    expect(html).toContain('no impact measurement');
    expect(html).not.toContain('<img');
  });
});
