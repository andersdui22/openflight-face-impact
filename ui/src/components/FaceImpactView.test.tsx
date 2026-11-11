import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { FaceImpactView } from './FaceImpactView';

const polygon: Array<[number, number]> = [
  [-50, -25],
  [50, -25],
  [40, 25],
  [-40, 25],
];

describe('FaceImpactView', () => {
  it('shows synthetic impact coordinates, regions and marker', () => {
    const html = renderToString(
      <FaceImpactView
        polygon={polygon}
        result={{
          status: 'ok',
          x_mm: 12,
          y_mm: 5,
          horizontal_region: 'toe',
          vertical_region: 'high',
        }}
      />
    );
    expect(html).toContain('Test data only');
    expect(html.replace(/<!-- -->/g, '')).toContain('12.0 mm');
    expect(html.replace(/<!-- -->/g, '')).toContain('5.0 mm');
    expect(html.replace(/<!-- -->/g, '')).toContain('toe / high');
    expect(html).toContain('synthetic-impact-marker');
    expect(html).toContain('<polygon');
    expect(html).toContain('stroke-dasharray="4 5"');
  });

  it('shows a rejection without a misleading impact marker', () => {
    const html = renderToString(
      <FaceImpactView
        polygon={polygon}
        result={{
          status: 'outside_face',
          rejection_reason: 'synthetic contact lies outside polygonal face',
        }}
      />
    );
    expect(html).toContain('Contact outside clubface');
    expect(html).not.toContain('synthetic-impact-marker');
    expect(html).not.toContain('X:');
  });

  it('rejects invalid displayed impact coordinates', () => {
    const html = renderToString(
      <FaceImpactView
        polygon={polygon}
        result={{
          status: 'ok',
          x_mm: Number.NaN,
          y_mm: 5,
          horizontal_region: 'toe',
          vertical_region: 'high',
        }}
      />
    );
    expect(html).toContain('Invalid impact coordinates');
    expect(html).not.toContain('synthetic-impact-marker');
  });

  it('never displays a point outside the supplied face outline', () => {
    const html = renderToString(
      <FaceImpactView polygon={polygon} result={{
        status: 'ok', x_mm: 90, y_mm: 0, horizontal_region: 'toe', vertical_region: 'center',
      }} />
    );
    expect(html).toContain('Impact point outside clubface outline');
    expect(html).not.toContain('synthetic-impact-marker');
    expect(html).not.toContain('X:');
  });

  it('never displays a point when the supplied face outline is invalid', () => {
    const html = renderToString(
      <FaceImpactView polygon={[[0, 0], [1, 0]]} result={{
        status: 'ok', x_mm: 0.5, y_mm: 0, horizontal_region: 'center', vertical_region: 'center',
      }} />
    );
    expect(html).toContain('Invalid clubface outline');
    expect(html).not.toContain('synthetic-impact-marker');
  });

  it('rejects a zero-area clubface outline without drawing a marker', () => {
    const html = renderToString(
      <FaceImpactView polygon={[[0, 0], [1, 1], [2, 2]]} result={{
        status: 'ok', x_mm: 1, y_mm: 1, horizontal_region: 'center', vertical_region: 'center',
      }} />
    );
    expect(html).toContain('Invalid clubface outline');
    expect(html).not.toContain('synthetic-impact-marker');
  });

  it('supports a nonrectangular face outline', () => {
    const html = renderToString(
      <FaceImpactView
        polygon={[
          [-50, -25],
          [50, -25],
          [40, 25],
          [-40, 25],
        ]}
        result={{ status: 'no_tangency', rejection_reason: 'No tangency' }}
      />
    );
    expect(html).toContain('No ball-to-face contact');
    expect(html).toContain('<polygon');
  });
});
