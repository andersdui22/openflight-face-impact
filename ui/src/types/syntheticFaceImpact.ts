import type { FaceImpactDisplayResult } from '../components/FaceImpactView';

export type SyntheticFaceImpactResponse =
  | {
      schema_version: 1;
      source: 'synthetic_python_pipeline';
      ok: true;
      case_id: string;
      label: string;
      polygon_face_mm: [number, number][];
      result: FaceImpactDisplayResult;
    }
  | {
      schema_version: 1;
      source: 'synthetic_python_pipeline';
      ok: false;
      error: string;
    };

export function isSyntheticFaceImpactResponse(value: unknown): value is SyntheticFaceImpactResponse {
  if (typeof value !== 'object' || value === null) return false;
  const data = value as Record<string, unknown>;
  if (data.schema_version !== 1 || data.source !== 'synthetic_python_pipeline') return false;
  if (data.ok === false) return typeof data.error === 'string';
  if (data.ok !== true || typeof data.case_id !== 'string' || !Array.isArray(data.polygon_face_mm)) return false;
  if (
    data.polygon_face_mm.length < 3 ||
    !data.polygon_face_mm.every(
      (point) =>
        Array.isArray(point) &&
        point.length === 2 &&
        point.every((coordinate) => typeof coordinate === 'number' && Number.isFinite(coordinate))
    )
  )
    return false;
  if (typeof data.result !== 'object' || data.result === null) return false;
  const result = data.result as Record<string, unknown>;
  if (result.status === 'ok') {
    return (
      typeof result.x_mm === 'number' &&
      Number.isFinite(result.x_mm) &&
      typeof result.y_mm === 'number' &&
      Number.isFinite(result.y_mm) &&
      ['heel', 'center', 'toe'].includes(String(result.horizontal_region)) &&
      ['low', 'center', 'high'].includes(String(result.vertical_region))
    );
  }
  return (
    ['outside_face', 'no_tangency', 'invalid_geometry'].includes(String(result.status)) &&
    typeof result.rejection_reason === 'string' &&
    result.x_mm === undefined &&
    result.y_mm === undefined
  );
}
