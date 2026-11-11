import { beforeEach, describe, expect, it } from 'vitest';
import { useOfflineImpactStore } from './useOfflineImpactStore';

const accepted = {
  schema_version: 1 as const,
  source: 'offline_synthetic_analysis' as const,
  shot_id: 'shot-1',
  session_id: 'session-1',
  accepted: true as const,
  reason: 'synthetic geometry only',
  physically_validated: false as const,
  position_uncertainty_mm: null,
  frame_index: 1,
  x_mm: 12,
  y_mm: 5,
  horizontal_region: 'toe' as const,
  vertical_region: 'high' as const,
};

describe('offline impact session ingestion', () => {
  beforeEach(() => useOfflineImpactStore.getState().clear());

  it('accepts a synthetic result without upgrading it to a measurement', () => {
    useOfflineImpactStore.getState().ingest(accepted);
    expect(useOfflineImpactStore.getState().entries).toEqual([accepted]);
  });

  it('ignores invalid messages and duplicate shot identifiers', () => {
    useOfflineImpactStore.getState().ingest(accepted);
    useOfflineImpactStore.getState().ingest({ ...accepted, x_mm: Number.NaN });
    useOfflineImpactStore.getState().ingest({ ...accepted, x_mm: 30 });
    expect(useOfflineImpactStore.getState().entries).toEqual([accepted]);
  });

  it('replaces prior session history on session identity change', () => {
    useOfflineImpactStore.getState().ingest(accepted);
    useOfflineImpactStore.getState().ingest({
      ...accepted, session_id: 'session-2', shot_id: 'shot-2',
    });
    expect(useOfflineImpactStore.getState().entries.map((entry) => entry.shot_id)).toEqual(['shot-2']);
  });

  it('retains rejection reasons without coordinates', () => {
    const rejected = {
      schema_version: 1, source: 'offline_synthetic_analysis',
      shot_id: 'shot-3', session_id: 'session-1', accepted: false,
      reason: 'ambiguous', physically_validated: false, position_uncertainty_mm: null,
    };
    useOfflineImpactStore.getState().ingest(rejected);
    expect(useOfflineImpactStore.getState().entries[0]).toEqual(rejected);
  });
});
