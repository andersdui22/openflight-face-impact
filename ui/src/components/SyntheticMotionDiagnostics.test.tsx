import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { SyntheticMotionDiagnostics, type SyntheticMotionPayload } from './SyntheticMotionDiagnostics';

const payload: SyntheticMotionPayload = {
  schema_version: 1,
  kind: 'synthetic_image_space_motion',
  physical_contact_confirmed: false,
  impact_frame_index: null,
  impact_x_mm: null,
  impact_y_mm: null,
  position_uncertainty_mm: null,
  closest_observed_frame_index: 1,
  has_observed_approach_and_separation: true,
  motion_reason: 'synthetic approach and separation only',
  proximity_reason: 'unique pixel minimum',
  rejected_frames: [],
  proximity_samples: [
    { frame_index: 0, sensor_timestamp_ns: 100, host_timestamp_ns: 1000, separation_px: 10 },
    { frame_index: 1, sensor_timestamp_ns: 200, host_timestamp_ns: 2000, separation_px: 2 },
    { frame_index: 2, sensor_timestamp_ns: 300, host_timestamp_ns: 3000, separation_px: 9 },
  ],
};

describe('SyntheticMotionDiagnostics', () => {
  it('shows safe empty state without backend payload', () => {
    const html = renderToString(<SyntheticMotionDiagnostics payload={null} />);
    expect(html).toContain('Awaiting offline synthetic camera analysis');
    expect(html).not.toContain('Closest observed frame:');
  });

  it('shows pixel trend without physical contact claims', () => {
    const html = renderToString(<SyntheticMotionDiagnostics payload={payload} />);
    expect(html).toContain('Closest observed frame:');
    expect(html).toContain('SYNTHETIC MOTION');
    expect(html).toContain('separation in pixels');
    expect(html).toContain('Physical impact and accuracy remain unverified');
    expect(html).toContain('<polyline');
    expect(html).toContain('Select observed frame');
    expect(html.replace(/<!-- -->/g, '')).toContain('Selected frame 2');
    expect(html.replace(/<!-- -->/g, '')).toContain('Separation 2.00 px');
  });

  it('rejects payloads that claim physical impact', () => {
    const unsafe = { ...payload, physical_contact_confirmed: true } as unknown as SyntheticMotionPayload;
    const html = renderToString(<SyntheticMotionDiagnostics payload={unsafe} />);
    expect(html).toContain('Awaiting offline synthetic camera analysis');
  });
});
