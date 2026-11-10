import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { FaceImpactCameraPreview } from './FaceImpactCameraPreview';

describe('FaceImpactCameraPreview', () => {
  it('starts with a checking state and never fabricates camera frames', () => {
    const html = renderToString(<FaceImpactCameraPreview />);
    expect(html).toContain('USB camera preview');
    expect(html).toContain('Camera: checking');
    expect(html).toContain('no impact measurement');
    expect(html).not.toContain('<img');
  });
});
