import { isOfflineImpactEvidence, type OfflineImpactEvidence } from './offlineImpactEvidence';

export type FacePoint = [number, number];

export type ClubStatistics = {
  club_id: string;
  outline_mm: FacePoint[];
  points_mm: FacePoint[];
  mean_mm: FacePoint | null;
  spread_mm: FacePoint | null;
  rejected_count: number;
};

type FrameQuality = {
  brightness_mean: number;
  contrast_span: number;
  dark_fraction: number;
  saturated_fraction: number;
};

export type ShotDiagnostic = {
  shot_id: string | null;
  club_id: string | null;
  status: 'accepted' | 'rejected' | 'invalid';
  reason: string;
  calibration?: { id: string; image_size_px: FacePoint };
  frames?: FrameQuality[];
  sensor_gap_ns?: FacePoint;
  host_gap_ns?: FacePoint;
  calculation_version?: string;
};

export type OfflineSessionAnalysis = {
  schema_version: 1;
  source: 'offline_synthetic_analysis';
  session_id: string;
  clubs: ClubStatistics[];
  evidence: OfflineImpactEvidence[];
  diagnostics: ShotDiagnostic[];
};

const finite = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);
const pair = (value: unknown): value is FacePoint => Array.isArray(value) && value.length === 2 && value.every(finite);

function validClub(club: ClubStatistics | null) {
  return (
    club &&
    typeof club.club_id === 'string' &&
    Array.isArray(club.outline_mm) &&
    club.outline_mm.length >= 3 &&
    club.outline_mm.every(pair) &&
    Array.isArray(club.points_mm) &&
    club.points_mm.every(pair) &&
    (club.mean_mm === null || pair(club.mean_mm)) &&
    (club.spread_mm === null || pair(club.spread_mm)) &&
    Number.isSafeInteger(club.rejected_count) &&
    club.rejected_count >= 0
  );
}

function validDiagnostic(item: ShotDiagnostic | null) {
  return (
    item &&
    (item.shot_id === null || typeof item.shot_id === 'string') &&
    (item.club_id === null || typeof item.club_id === 'string') &&
    ['accepted', 'rejected', 'invalid'].includes(item.status) &&
    typeof item.reason === 'string' &&
    (item.calibration === undefined ||
      (typeof item.calibration?.id === 'string' && pair(item.calibration.image_size_px))) &&
    (item.sensor_gap_ns === undefined || pair(item.sensor_gap_ns)) &&
    (item.host_gap_ns === undefined || pair(item.host_gap_ns)) &&
    (item.calculation_version === undefined || typeof item.calculation_version === 'string') &&
    (item.frames === undefined ||
      (Array.isArray(item.frames) &&
        item.frames.every((frame) =>
          [frame?.brightness_mean, frame?.contrast_span, frame?.dark_fraction, frame?.saturated_fraction].every(finite)
        )))
  );
}

export function isOfflineSessionAnalysis(value: unknown, sessionId: string): value is OfflineSessionAnalysis {
  if (typeof value !== 'object' || value === null) return false;
  const report = value as Partial<OfflineSessionAnalysis>;
  return (
    report.schema_version === 1 &&
    report.source === 'offline_synthetic_analysis' &&
    report.session_id === sessionId &&
    Array.isArray(report.evidence) &&
    report.evidence.every(isOfflineImpactEvidence) &&
    report.evidence.every((entry) => entry.session_id === sessionId) &&
    new Set(report.evidence.map((entry) => entry.shot_id)).size === report.evidence.length &&
    Array.isArray(report.clubs) &&
    report.clubs.every(validClub) &&
    Array.isArray(report.diagnostics) &&
    report.diagnostics.every(validDiagnostic)
  );
}
