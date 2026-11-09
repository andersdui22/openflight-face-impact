import { useEffect, useState } from 'react';
import { FaceImpactView } from './FaceImpactView';
import { socketService } from '../services/socketService';
import type { SyntheticFaceImpactResponse } from '../types/syntheticFaceImpact';

const cases = [
  { id: 'toe-high', label: 'Toe / high' },
  { id: 'heel-low', label: 'Heel / low' },
  { id: 'outside-face', label: 'Outside face' },
  { id: 'no-tangency', label: 'No tangency' },
];

export function SyntheticFaceImpactDemo() {
  const [selectedId, setSelectedId] = useState(cases[0].id);
  const [revision, setRevision] = useState(0);
  const [response, setResponse] = useState<SyntheticFaceImpactResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    socketService
      .requestSyntheticFaceImpact(selectedId)
      .then((payload) => {
        if (!active) return;
        if (payload.ok) {
          setResponse(payload);
          setError(null);
        } else {
          setResponse(null);
          setError(payload.error);
        }
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setResponse(null);
        setError(reason instanceof Error ? reason.message : 'Synthetic request failed');
      });
    return () => {
      active = false;
    };
  }, [selectedId, revision]);

  return (
    <div>
      <label htmlFor="synthetic-face-impact-case">Synthetic Face Impact test case</label>
      <select
        id="synthetic-face-impact-case"
        value={selectedId}
        onChange={(event) => {
          setResponse(null);
          setError(null);
          setSelectedId(event.target.value);
        }}
        style={{ display: 'block', margin: 'var(--space-sm) 0' }}
      >
        {cases.map((scenario) => (
          <option key={scenario.id} value={scenario.id}>
            {scenario.label}
          </option>
        ))}
      </select>
      <button type="button" onClick={() => setRevision((value) => value + 1)}>
        Request synthetic result
      </button>
      <p>Python backend synthetic calculation · Not a camera measurement</p>
      {error && <p role="alert">{error}</p>}
      {!error && !response && <p role="status">Waiting for synthetic backend result…</p>}
      {response?.ok && <FaceImpactView polygon={response.polygon_face_mm} result={response.result} />}
    </div>
  );
}
