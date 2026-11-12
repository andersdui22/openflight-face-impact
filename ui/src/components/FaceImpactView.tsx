import type { CSSProperties } from 'react';

export type FaceImpactDisplayResult =
  | {
      status: 'ok';
      x_mm: number;
      y_mm: number;
      horizontal_region: 'heel' | 'center' | 'toe';
      vertical_region: 'low' | 'center' | 'high';
    }
  | {
      status: 'outside_face' | 'no_tangency' | 'invalid_geometry';
      rejection_reason: string;
    };

interface FaceImpactViewProps {
  /** Explicit synthetic face outline in local heel/toe and vertical millimetres. */
  polygon: ReadonlyArray<readonly [number, number]>;
  result: FaceImpactDisplayResult;
}

const surface: CSSProperties = {
  border: '1px solid var(--color-border)',
  borderRadius: 'var(--radius)',
  background: 'var(--color-surface)',
  padding: 'var(--space-md)',
  color: 'var(--color-text)',
};

const reasons: Record<Exclude<FaceImpactDisplayResult['status'], 'ok'>, string> = {
  outside_face: 'Contact outside clubface',
  no_tangency: 'No ball-to-face contact',
  invalid_geometry: 'Invalid input geometry',
};

export function FaceImpactView({ polygon, result }: FaceImpactViewProps) {
  const validPolygon =
    polygon.length >= 3 &&
    polygon.length <= 128 &&
    polygon.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y)) &&
    Math.abs(
      polygon.reduce((sum, [x, y], i) => {
        const [nextX, nextY] = polygon[(i + 1) % polygon.length];
        return sum + x * nextY - y * nextX;
      }, 0)
    ) > 1e-8;
  const finiteImpact = result.status === 'ok' && Number.isFinite(result.x_mm) && Number.isFinite(result.y_mm);
  const xs = polygon.map(([x]) => x);
  const ys = polygon.map(([, y]) => y);
  const minX = validPolygon ? Math.min(...xs) : -50;
  const maxX = validPolygon ? Math.max(...xs) : 50;
  const minY = validPolygon ? Math.min(...ys) : -25;
  const maxY = validPolygon ? Math.max(...ys) : 25;
  const spanX = Math.max(1, maxX - minX);
  const spanY = Math.max(1, maxY - minY);
  const scale = Math.min(240 / spanX, 120 / spanY);
  const toScreen = ([x, y]: readonly [number, number]): [number, number] => [
    160 + (x - (minX + maxX) / 2) * scale,
    85 - (y - (minY + maxY) / 2) * scale,
  ];
  const outline = validPolygon ? polygon.map((point) => toScreen(point).join(',')).join(' ') : '';
  // A synthetic point outside the provided polygon must not be rendered as a valid hit.
  const pointInside = (x: number, y: number): boolean => {
    let inside = false;
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const [xi, yi] = polygon[i];
      const [xj, yj] = polygon[j];
      const cross = (x - xi) * (yj - yi) - (y - yi) * (xj - xi);
      const onEdge =
        Math.abs(cross) < 1e-8 &&
        x >= Math.min(xi, xj) &&
        x <= Math.max(xi, xj) &&
        y >= Math.min(yi, yj) &&
        y <= Math.max(yi, yj);
      if (onEdge) return true;
      if (yi > y !== yj > y && x < xi + ((y - yi) * (xj - xi)) / (yj - yi)) inside = !inside;
    }
    return inside;
  };
  const validImpact = validPolygon && result.status === 'ok' && finiteImpact && pointInside(result.x_mm, result.y_mm);
  const impactPoint = validImpact && result.status === 'ok' ? toScreen([result.x_mm, result.y_mm]) : null;
  const rejection =
    result.status !== 'ok'
      ? reasons[result.status]
      : !validPolygon
        ? 'Invalid clubface outline'
        : !finiteImpact
          ? 'Invalid impact coordinates'
          : !validImpact
            ? 'Impact point outside clubface outline'
            : null;

  return (
    <section style={surface} aria-label="Synthetic Face Impact">
      <h3 style={{ margin: '0 0 var(--space-sm)' }}>Face Impact — synthetic preview</h3>
      <p style={{ color: 'var(--color-text-muted)', margin: '0 0 var(--space-sm)' }}>
        Test data only · Not a camera measurement
      </p>
      <svg
        viewBox="0 0 320 170"
        role="img"
        aria-label={rejection ? `No impact: ${rejection}` : 'Synthetic clubface and impact location'}
        style={{ display: 'block', width: '100%', maxHeight: 260 }}
      >
        <rect x="0" y="0" width="320" height="170" rx="4" fill="var(--color-bg)" />
        {validPolygon && (
          <polygon points={outline} fill="var(--color-surface)" stroke="var(--color-text-muted)" strokeWidth="2" />
        )}
        {validPolygon && (
          <>
            <line
              x1={toScreen([(minX + maxX) / 2, minY])[0]}
              y1={toScreen([(minX + maxX) / 2, minY])[1]}
              x2={toScreen([(minX + maxX) / 2, maxY])[0]}
              y2={toScreen([(minX + maxX) / 2, maxY])[1]}
              stroke="var(--color-text-muted)"
              strokeDasharray="4 5"
              opacity="0.6"
            />
            <line
              x1={toScreen([minX, (minY + maxY) / 2])[0]}
              y1={toScreen([minX, (minY + maxY) / 2])[1]}
              x2={toScreen([maxX, (minY + maxY) / 2])[0]}
              y2={toScreen([maxX, (minY + maxY) / 2])[1]}
              stroke="var(--color-text-muted)"
              strokeDasharray="4 5"
              opacity="0.6"
            />
          </>
        )}
        {impactPoint && (
          <circle
            cx={impactPoint[0]}
            cy={impactPoint[1]}
            r="5"
            fill="var(--color-accent)"
            stroke="var(--color-text)"
            strokeWidth="1.5"
            data-testid="synthetic-impact-marker"
          />
        )}
        <text x="10" y="162" fontSize="11" fill="var(--color-text-muted)">
          HEEL
        </text>
        <text x="280" y="162" fontSize="11" fill="var(--color-text-muted)">
          TOE
        </text>
      </svg>
      {validImpact && result.status === 'ok' && (
        <p style={{ margin: 'var(--space-sm) 0 0' }} aria-live="polite">
          X: {result.x_mm.toFixed(1)} mm · Y: {result.y_mm.toFixed(1)} mm · {result.horizontal_region} /{' '}
          {result.vertical_region}
        </p>
      )}
      {rejection && (
        <p role="status" style={{ color: 'var(--color-warning)', margin: 'var(--space-sm) 0 0' }}>
          {rejection}
        </p>
      )}
    </section>
  );
}
