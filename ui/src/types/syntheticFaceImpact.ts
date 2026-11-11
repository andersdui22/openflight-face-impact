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
  if (data.ok === false) {
    return typeof data.error === 'string' && data.error.trim().length > 0 &&
      data.result === undefined && data.polygon_face_mm === undefined;
  }
  if (data.ok !== true || typeof data.case_id !== 'string' ||
      !data.case_id.trim() || typeof data.label !== 'string' ||
      !data.label.trim() || !Array.isArray(data.polygon_face_mm)) return false;
  if (
    data.polygon_face_mm.length < 3 ||
    data.polygon_face_mm.length > 128 ||
    !data.polygon_face_mm.every(
      (point) =>
        Array.isArray(point) &&
        point.length === 2 &&
        point.every((coordinate) => typeof coordinate === 'number' && Number.isFinite(coordinate))
    )
  )
    return false;
  const vertices = data.polygon_face_mm as [number, number][];
  const signedAreaTwice = vertices.reduce((sum, [x, y], i) => {
    const [nextX, nextY] = vertices[(i + 1) % vertices.length];
    return sum + x * nextY - y * nextX;
  }, 0);
  if (!Number.isFinite(signedAreaTwice) || Math.abs(signedAreaTwice) <= 1e-8) return false;
  // Reject self-intersecting face outlines: a nonzero shoelace area alone is insufficient.
  const orientation = (a: [number, number], b: [number, number], c: [number, number]) =>
    (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const intersects = (a: [number, number], b: [number, number],
    c: [number, number], d: [number, number]) => {
    const o1 = orientation(a, b, c);
    const o2 = orientation(a, b, d);
    const o3 = orientation(c, d, a);
    const o4 = orientation(c, d, b);
    return o1 * o2 < 0 && o3 * o4 < 0;
  };
  for (let i = 0; i < vertices.length; i++) {
    for (let j = i + 2; j < vertices.length; j++) {
      if (i === 0 && j === vertices.length - 1) continue;
      if (intersects(vertices[i], vertices[(i + 1) % vertices.length],
        vertices[j], vertices[(j + 1) % vertices.length])) return false;
    }
  }
  if (typeof data.result !== 'object' || data.result === null) return false;
  const result = data.result as Record<string, unknown>;
  if (result.status === 'ok') {
    if (typeof result.x_mm !== 'number' || typeof result.y_mm !== 'number') return false;
    const x = result.x_mm;
    const y = result.y_mm;
    let inside = false;
    for (let i = 0, j = vertices.length - 1; i < vertices.length; j = i++) {
      const [xi, yi] = vertices[i];
      const [xj, yj] = vertices[j];
      const cross = (x - xi) * (yj - yi) - (y - yi) * (xj - xi);
      if (Math.abs(cross) < 1e-8 &&
        x >= Math.min(xi, xj) && x <= Math.max(xi, xj) &&
        y >= Math.min(yi, yj) && y <= Math.max(yi, yj)) {
        inside = true;
        break;
      }
      if ((yi > y) !== (yj > y) && x < xi + ((y - yi) * (xj - xi)) / (yj - yi)) inside = !inside;
    }
    return inside && result.rejection_reason === undefined && (
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
    result.y_mm === undefined &&
    result.horizontal_region === undefined &&
    result.vertical_region === undefined
  );
}
