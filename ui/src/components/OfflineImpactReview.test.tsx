import { beforeEach, describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { OfflineImpactReview } from './OfflineImpactReview';
import { useOfflineImpactStore } from '../stores/useOfflineImpactStore';

const accepted = {
  schema_version: 1 as const,
  source: 'offline_synthetic_analysis' as const,
  shot_id: 'shot-a',
  session_id: 'session-a',
  accepted: true as const,
  reason: 'synthetic geometry',
  physically_validated: false as const,
  position_uncertainty_mm: null,
  frame_index: 1,
  x_mm: 12,
  y_mm: 5,
  horizontal_region: 'toe' as const,
  vertical_region: 'high' as const,
};

describe('offline synthetic impact review', () => {
  beforeEach(() => useOfflineImpactStore.getState().clear());

  it('renders a synthetic marker and source identity for accepted evidence', () => {
    useOfflineImpactStore.getState().ingest(accepted);
    const html = renderToStaticMarkup(<OfflineImpactReview evidence={useOfflineImpactStore.getState().entries} />);
    expect(html).toContain('shot-a');
    expect(html).toContain('NOT CAMERA MEASUREMENTS');
    expect(html).toContain('synthetic-impact-marker');
  });

  it('never draws an impact marker for rejected evidence', () => {
    useOfflineImpactStore.getState().ingest({
      schema_version: 1, source: 'offline_synthetic_analysis',
      shot_id: 'shot-b', session_id: 'session-a', accepted: false,
      reason: 'ambiguous frame', physically_validated: false, position_uncertainty_mm: null,
    });
    const html = renderToStaticMarkup(<OfflineImpactReview evidence={useOfflineImpactStore.getState().entries} />);
    expect(html).toContain('ambiguous frame');
    expect(html).not.toContain('synthetic-impact-marker');
  });

  it('does not show the earlier accepted marker when the latest shot is rejected', () => {
    useOfflineImpactStore.getState().ingest(accepted);
    useOfflineImpactStore.getState().ingest({
      schema_version: 1, source: 'offline_synthetic_analysis',
      shot_id: 'shot-rejected', session_id: 'session-a', accepted: false,
      reason: 'no unique temporal contact', physically_validated: false,
      position_uncertainty_mm: null,
    });
    const html = renderToStaticMarkup(
      <OfflineImpactReview evidence={useOfflineImpactStore.getState().entries} />
    );
    expect(html).toContain('shot-a');
    expect(html).toContain('shot-rejected');
    expect(html).toContain('no unique temporal contact');
    expect(html).not.toContain('data-testid="synthetic-impact-marker"');
  });

  it('does not draw outside the illustrative reference outline', () => {
    useOfflineImpactStore.getState().ingest({ ...accepted, x_mm: 200 });
    const html = renderToStaticMarkup(<OfflineImpactReview evidence={useOfflineImpactStore.getState().entries} />);
    expect(html).toContain('no marker displayed');
    expect(html).not.toContain('synthetic-impact-marker');
  });
});
