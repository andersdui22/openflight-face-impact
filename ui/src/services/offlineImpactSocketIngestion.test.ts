import { beforeEach, describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ingestOfflineImpactSocketEvent } from './offlineImpactSocketIngestion';
import { OfflineImpactReview } from '../components/OfflineImpactReview';
import { useOfflineImpactStore } from '../stores/useOfflineImpactStore';

const pythonPayload = {
  schema_version: 1,
  source: 'offline_synthetic_analysis',
  shot_id: 'synthetic-shot',
  session_id: 'synthetic-session',
  accepted: true,
  reason: 'accepted for offline analysis',
  physically_validated: false,
  position_uncertainty_mm: null,
  frame_index: 1,
  x_mm: 12,
  y_mm: 5,
  horizontal_region: 'toe',
  vertical_region: 'high',
};

describe('offline socket event -> Zustand -> review contract', () => {
  beforeEach(() => useOfflineImpactStore.getState().clear());

  it('renders accepted Python schema v1 coordinates as synthetic only', () => {
    ingestOfflineImpactSocketEvent(pythonPayload);
    const entries = useOfflineImpactStore.getState().entries;
    expect(entries).toHaveLength(1);
    const html = renderToStaticMarkup(<OfflineImpactReview evidence={entries} />);
    expect(html).toContain('synthetic-shot');
    expect(html).toContain('X: <!-- -->12.0');
    expect(html).toContain('synthetic-impact-marker');
    expect(html).toContain('NOT CAMERA MEASUREMENTS');
  });

  it('rejects a forged physical-validation flag before rendering', () => {
    ingestOfflineImpactSocketEvent({ ...pythonPayload, physically_validated: true });
    expect(useOfflineImpactStore.getState().entries).toHaveLength(0);
  });

  it('shows rejection reason and no marker', () => {
    const { frame_index: _frame, x_mm: _x, y_mm: _y,
      horizontal_region: _horizontal, vertical_region: _vertical, ...rejected } = pythonPayload;
    ingestOfflineImpactSocketEvent({ ...rejected, accepted: false, reason: 'ambiguous frame' });
    const html = renderToStaticMarkup(
      <OfflineImpactReview evidence={useOfflineImpactStore.getState().entries} />
    );
    expect(html).toContain('ambiguous frame');
    expect(html).not.toContain('synthetic-impact-marker');
  });
});
