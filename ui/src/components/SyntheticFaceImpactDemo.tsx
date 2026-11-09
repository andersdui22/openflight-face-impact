import { useState } from 'react';
import { FaceImpactView, type FaceImpactDisplayResult } from './FaceImpactView';
import fixtures from '../data/syntheticFaceImpactCases.json';

// Gate 20: these are Python-verified static scenarios, NOT a live backend stream.
const cases = fixtures.cases;
const polygon: Array<[number, number]> = fixtures.polygon_face_mm.map(([x, y]) => [x, y]);

export function SyntheticFaceImpactDemo() {
  const [selectedId, setSelectedId] = useState(cases[0].id);
  const selected = cases.find((scenario) => scenario.id === selectedId) ?? cases[0];

  return (
    <div>
      <label htmlFor="synthetic-face-impact-case">Synthetic Face Impact test case</label>
      <select
        id="synthetic-face-impact-case"
        value={selectedId}
        onChange={(event) => setSelectedId(event.target.value)}
        style={{ display: 'block', margin: 'var(--space-sm) 0' }}
      >
        {cases.map((scenario) => (
          <option key={scenario.id} value={scenario.id}>
            {scenario.label}
          </option>
        ))}
      </select>
      <FaceImpactView polygon={polygon} result={selected.result as FaceImpactDisplayResult} />
    </div>
  );
}
