/** Version 1 Python offline synthetic impact export. No physical impact claim. */
export type OfflineImpactEvidence =
  | {
      schema_version: 1;
      source: 'offline_synthetic_analysis';
      shot_id: string;
      session_id: string;
      accepted: true;
      reason: string;
      physically_validated: false;
      position_uncertainty_mm: null;
      frame_index: number;
      x_mm: number;
      y_mm: number;
      horizontal_region: 'heel' | 'center' | 'toe';
      vertical_region: 'low' | 'center' | 'high';
    }
  | {
      schema_version: 1;
      source: 'offline_synthetic_analysis';
      shot_id: string;
      session_id: string;
      accepted: false;
      reason: string;
      physically_validated: false;
      position_uncertainty_mm: null;
    };

export function isOfflineImpactEvidence(value: unknown): value is OfflineImpactEvidence {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const data = value as Record<string, unknown>;
  if (
    data.schema_version !== 1 ||
    data.source !== 'offline_synthetic_analysis' ||
    typeof data.shot_id !== 'string' ||
    !data.shot_id.trim() ||
    typeof data.session_id !== 'string' ||
    !data.session_id.trim() ||
    typeof data.reason !== 'string' ||
    !data.reason.trim() ||
    data.physically_validated !== false ||
    data.position_uncertainty_mm !== null
  )
    return false;
  const fields = ['frame_index', 'x_mm', 'y_mm', 'horizontal_region', 'vertical_region'];
  if (data.accepted === false) return fields.every((field) => data[field] === undefined);
  if (data.accepted !== true) return false;
  return (
    Number.isSafeInteger(data.frame_index) &&
    (data.frame_index as number) >= 0 &&
    typeof data.x_mm === 'number' &&
    Number.isFinite(data.x_mm) &&
    typeof data.y_mm === 'number' &&
    Number.isFinite(data.y_mm) &&
    ['heel', 'center', 'toe'].includes(String(data.horizontal_region)) &&
    ['low', 'center', 'high'].includes(String(data.vertical_region))
  );
}
