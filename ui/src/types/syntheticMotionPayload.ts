/** Strictly synthetic, pixel-space motion data. Never physical impact. */
export type SyntheticMotionPayload = {
  schema_version: 1;
  kind: 'synthetic_image_space_motion';
  physical_contact_confirmed: false;
  impact_frame_index: null;
  impact_x_mm: null;
  impact_y_mm: null;
  position_uncertainty_mm: null;
  closest_observed_frame_index: number | null;
  has_observed_approach_and_separation: boolean;
  motion_reason: string;
  proximity_reason: string;
  rejected_frames: { frame_index: number; reason: string }[];
  proximity_samples: {
    frame_index: number;
    sensor_timestamp_ns: number;
    host_timestamp_ns: number;
    separation_px: number;
  }[];
};

export function isSyntheticMotionPayload(value: unknown): value is SyntheticMotionPayload {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const v = value as Record<string, unknown>;
  if (v.schema_version !== 1 || v.kind !== 'synthetic_image_space_motion' ||
      v.physical_contact_confirmed !== false || v.impact_frame_index !== null ||
      v.impact_x_mm !== null || v.impact_y_mm !== null ||
      v.position_uncertainty_mm !== null) return false;
  if (v.closest_observed_frame_index !== null &&
      (!Number.isSafeInteger(v.closest_observed_frame_index) || Number(v.closest_observed_frame_index) < 0)) return false;
  if (typeof v.has_observed_approach_and_separation !== 'boolean' ||
      typeof v.motion_reason !== 'string' || typeof v.proximity_reason !== 'string' ||
      !Array.isArray(v.rejected_frames) || !Array.isArray(v.proximity_samples) ||
      v.proximity_samples.length > 32 || v.rejected_frames.length > 32) return false;
  if (!v.rejected_frames.every((entry: unknown) => {
    if (typeof entry !== 'object' || entry === null) return false;
    const item = entry as Record<string, unknown>;
    return Number.isSafeInteger(item.frame_index) && Number(item.frame_index) >= 0 && typeof item.reason === 'string';
  })) return false;
  if (!v.proximity_samples.every((entry: unknown) => {
    if (typeof entry !== 'object' || entry === null) return false;
    const item = entry as Record<string, unknown>;
    return Number.isSafeInteger(item.frame_index) && Number(item.frame_index) >= 0 &&
      Number.isFinite(item.sensor_timestamp_ns) && Number.isFinite(item.host_timestamp_ns) &&
      typeof item.separation_px === 'number' && Number.isFinite(item.separation_px) && item.separation_px >= 0;
  })) return false;
  const samples = v.proximity_samples as { frame_index: number }[];
  if (new Set(samples.map((s) => s.frame_index)).size !== samples.length) return false;
  if (v.has_observed_approach_and_separation &&
      (v.closest_observed_frame_index === null ||
       !samples.some((s) => s.frame_index === v.closest_observed_frame_index))) return false;
  return true;
}
