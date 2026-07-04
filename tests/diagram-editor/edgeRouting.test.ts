import { describe, expect, it } from 'vitest';
import { buildOrthogonalPath } from '@/features/diagram-editor/utils/edgeRouting';

describe('edgeRouting', () => {
  it('builds an orthogonal path with source and target stubs', () => {
    expect(
      buildOrthogonalPath(
        { x: 0, y: 10 },
        'right',
        { x: 100, y: 50 },
        'left',
        { stubLength: 10 },
      ),
    ).toBe('M 0 10 L 10 10 L 50 10 L 50 50 L 90 50 L 100 50');
  });

  it('chooses a vertical middle route when vertical distance dominates', () => {
    expect(
      buildOrthogonalPath(
        { x: 10, y: 0 },
        'bottom',
        { x: 40, y: 120 },
        'top',
        { stubLength: 10 },
      ),
    ).toBe('M 10 0 L 10 10 L 10 60 L 40 60 L 40 110 L 40 120');
  });

  it('routes same-side bottom ports through a single shared bus line', () => {
    expect(
      buildOrthogonalPath(
        { x: 0, y: 100 },
        'bottom',
        { x: 80, y: 70 },
        'bottom',
        { stubLength: 10 },
      ),
    ).toBe('M 0 100 L 0 110 L 80 110 L 80 70');
  });

  it('routes a horizontal bus to a bottom port without a staircase', () => {
    expect(
      buildOrthogonalPath(
        { x: 0, y: 100 },
        'right',
        { x: 80, y: 70 },
        'bottom',
        { stubLength: 10 },
      ),
    ).toBe('M 0 100 L 10 100 L 80 100 L 80 70');
  });
});
