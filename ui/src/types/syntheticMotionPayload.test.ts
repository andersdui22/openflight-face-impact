import { describe, expect, it } from 'vitest';
import { isSyntheticMotionPayload } from './syntheticMotionPayload';

const valid = {
  schema_version: 1,
  kind: 'synthetic_image_space_motion',
  physical_contact_confirmed: false,
  impact_frame_index: null,
  impact_x_mm: null,
  impact_y_mm: null,
  position_uncertainty_mm: null,
  closest_observed_frame_index: 1,
  has_observed_approach_and_separation: true,
  motion_reason: 'synthetic',
  proximity_reason: 'minimum',
  rejected_frames: [],
  proximity_samples: [{ frame_index: 1, sensor_timestamp_ns: 1, host_timestamp_ns: 2, separation_px: 4 }],
};

describe('synthetic motion websocket payload validation', () => {
  it('accepts strictly synthetic evidence', () => expect(isSyntheticMotionPayload(valid)).toBe(true));
  it('rejects physical contact claims', () =>
    expect(isSyntheticMotionPayload({ ...valid, physical_contact_confirmed: true })).toBe(false));
  it('rejects missing trend samples', () =>
    expect(isSyntheticMotionPayload({ ...valid, proximity_samples: [] })).toBe(false));
  it('rejects invalid pixel distances', () =>
    expect(
      isSyntheticMotionPayload({ ...valid, proximity_samples: [{ ...valid.proximity_samples[0], separation_px: -1 }] })
    ).toBe(false));
});
