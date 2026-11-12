import { useState } from 'react';
import type {
  ClubStatistics,
  OfflineSessionAnalysis as SessionReport,
  ShotDiagnostic,
} from '../types/offlineSessionAnalysis';

function ImpactDistribution({ club }: { club: ClubStatistics }) {
  const xs = club.outline_mm.map(([x]) => x);
  const ys = club.outline_mm.map(([, y]) => y);
  const left = Math.min(...xs);
  const top = Math.max(...ys);
  const width = Math.max(...xs) - left;
  const height = top - Math.min(...ys);
  return (
    <svg
      role="img"
      aria-label="Synthetic impact distribution in millimetres"
      viewBox={`${left - 5} ${-top - 5} ${width + 10} ${height + 10}`}
      style={{ display: 'block', width: '100%', maxHeight: '12rem' }}
    >
      <polygon points={club.outline_mm.map(([x, y]) => `${x},${-y}`).join(' ')} fill="none" stroke="currentColor" />
      {club.points_mm.map(([x, y], index) => (
        <circle key={index} cx={x} cy={-y} r="1.5" fill="var(--color-accent)" />
      ))}
    </svg>
  );
}

const formatPair = (value: [number, number]) => `X ${value[0].toFixed(2)} mm · Y ${value[1].toFixed(2)} mm`;

function Diagnostics({ shot }: { shot: ShotDiagnostic }) {
  const gap = (value: [number, number]) => `${(value[0] / 1e6).toFixed(2)}–${(value[1] / 1e6).toFixed(2)} ms`;
  return (
    <li>
      <p>
        <strong>{shot.status === 'invalid' ? 'Invalid record' : `Synthetic ${shot.status}`}</strong>
        {' · '}
        {shot.shot_id ?? 'Unknown shot'} · {shot.reason}
      </p>
      {shot.calibration && (
        <p>
          Calibration {shot.calibration.id} · {shot.calibration.image_size_px.join(' × ')} px
        </p>
      )}
      {shot.sensor_gap_ns && <p>Sensor intervals {gap(shot.sensor_gap_ns)}</p>}
      {shot.host_gap_ns && <p>Host arrival intervals {gap(shot.host_gap_ns)}</p>}
      {shot.calculation_version && <p>Calculation {shot.calculation_version}</p>}
      {shot.frames && (
        <ol aria-label="Saved frame quality">
          {shot.frames.map((frame, index) => (
            <li key={index}>
              Brightness {frame.brightness_mean.toFixed(1)}/255 · contrast {frame.contrast_span.toFixed(1)}/255 · dark{' '}
              {(frame.dark_fraction * 100).toFixed(1)}% · saturated {(frame.saturated_fraction * 100).toFixed(1)}%
            </li>
          ))}
        </ol>
      )}
    </li>
  );
}

export function OfflineSessionAnalysis({ report }: { report: SessionReport }) {
  const [clubFilter, setClubFilter] = useState('');
  const clubs = report.clubs.filter((club) => !clubFilter || club.club_id === clubFilter);
  const invalid = report.diagnostics.filter((shot) => shot.status === 'invalid').length;
  return (
    <section aria-label="Saved synthetic session analysis">
      <p>
        Synthetic session {report.session_id} · {invalid} invalid record(s) excluded
      </p>
      <div className="impact-controls__fields">
        <label htmlFor="offline-analysis-club">Club model</label>
        <select id="offline-analysis-club" value={clubFilter} onChange={(event) => setClubFilter(event.target.value)}>
          <option value="">All clubs</option>
          {report.clubs.map((club) => (
            <option key={club.club_id}>{club.club_id}</option>
          ))}
        </select>
      </div>
      {clubs.map((club) => (
        <section key={club.club_id} aria-label={`Statistics for ${club.club_id}`}>
          <h4>{club.club_id}</h4>
          <p>
            Saved shots {club.points_mm.length + club.rejected_count} · Accepted {club.points_mm.length} · Rejected{' '}
            {club.rejected_count}
          </p>
          <p>Mean impact {club.mean_mm ? formatPair(club.mean_mm) : 'unavailable'}</p>
          <p>
            Spread (standard deviation) {club.spread_mm ? formatPair(club.spread_mm) : 'requires two accepted shots'}
          </p>
          {club.points_mm.length > 0 && <ImpactDistribution club={club} />}
        </section>
      ))}
      <details open={invalid > 0}>
        <summary>Session diagnostics</summary>
        <ul>
          {report.diagnostics
            .filter((shot) => !clubFilter || shot.club_id === clubFilter || shot.status === 'invalid')
            .map((shot, index) => (
              <Diagnostics key={index} shot={shot} />
            ))}
        </ul>
      </details>
    </section>
  );
}
