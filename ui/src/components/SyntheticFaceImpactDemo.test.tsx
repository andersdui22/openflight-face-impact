import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { SyntheticFaceImpactDemo } from './SyntheticFaceImpactDemo';
import fixtures from '../data/syntheticFaceImpactCases.json';

describe('SyntheticFaceImpactDemo', () => {
  it('renders the Python-verified first scenario and offers rejection cases', () => {
    const html = renderToString(<SyntheticFaceImpactDemo />).replace(/<!-- -->/g, '');
    expect(html).toContain('Synthetic Face Impact test case');
    expect(html).toContain('12.0 mm');
    expect(html).toContain('5.0 mm');
    expect(html).toContain('Outside face');
    expect(html).toContain('No tangency');
    expect(html).toContain('Test data only');
  });

  it('never supplies coordinates in rejected fixture results', () => {
    for (const scenario of fixtures.cases) {
      if (scenario.result.status !== 'ok') {
        expect(scenario.result).not.toHaveProperty('x_mm');
        expect(scenario.result).not.toHaveProperty('y_mm');
      }
    }
  });
  it('diagnostic: capture canonical fixture JSON formatting', async () => {
    const prettier = await import('prettier');
    const fs = await import('node:fs');
    const path = 'src/data/syntheticFaceImpactCases.json';
    const source = fs.readFileSync(path, 'utf8');
    const config = await prettier.resolveConfig(path);
    const formatted = await prettier.format(source, { ...config, filepath: path });
    console.log('GATE20_JSON_START' + JSON.stringify(formatted) + 'GATE20_JSON_END');
    expect(formatted.length).toBeGreaterThan(0);
  });
});
