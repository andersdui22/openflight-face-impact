import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { SyntheticFaceImpactDemo } from './SyntheticFaceImpactDemo';
import { isSyntheticFaceImpactResponse } from '../types/syntheticFaceImpact';

describe('SyntheticFaceImpactDemo', () => {
  it('renders the backend request control without fabricating an impact', () => {
    const html = renderToString(<SyntheticFaceImpactDemo />).replace(/<!-- -->/g, '');
    expect(html).toContain('Synthetic Face Impact test case');
    expect(html).toContain('Request synthetic result');
    expect(html).toContain('Not a camera measurement');
    expect(html).toContain('Waiting for synthetic backend result');
    expect(html).not.toContain('synthetic-impact-marker');
    expect(html).not.toContain('X:');
  });

  it('validates successful backend contract and rejects partial measurements', () => {
    const valid = {
      schema_version: 1,
      source: 'synthetic_python_pipeline',
      ok: true,
      case_id: 'toe-high',
      label: 'Toe / high',
      polygon_face_mm: [
        [-50, -25],
        [50, -25],
        [40, 25],
      ],
      result: {
        status: 'ok',
        x_mm: 12,
        y_mm: 5,
        horizontal_region: 'toe',
        vertical_region: 'high',
      },
    };
    expect(isSyntheticFaceImpactResponse(valid)).toBe(true);
    expect(isSyntheticFaceImpactResponse({ ...valid, result: { status: 'ok', x_mm: 12 } })).toBe(false);
    expect(isSyntheticFaceImpactResponse({ ...valid, polygon_face_mm: [[0, 0]] })).toBe(false);
    expect(isSyntheticFaceImpactResponse({ ...valid, polygon_face_mm: [[0, 0], [1, 1], [2, 2]] })).toBe(false);
    expect(isSyntheticFaceImpactResponse({ ...valid, result: { ...valid.result, x_mm: 500 } })).toBe(false);
    expect(isSyntheticFaceImpactResponse({ ...valid, result: { ...valid.result, x_mm: Number.NaN } })).toBe(false);
  });

  it('rejects contact coordinates in a rejected result', () => {
    const base = {
      schema_version: 1,
      source: 'synthetic_python_pipeline',
      ok: true,
      case_id: 'outside-face',
      label: 'Outside face',
      polygon_face_mm: [
        [-50, -25],
        [50, -25],
        [40, 25],
      ],
    };
    expect(
      isSyntheticFaceImpactResponse({
        ...base,
        result: { status: 'outside_face', rejection_reason: 'outside' },
      })
    ).toBe(true);
    expect(
      isSyntheticFaceImpactResponse({
        ...base,
        result: { status: 'outside_face', rejection_reason: 'outside', x_mm: 0 },
      })
    ).toBe(false);
  });
});
