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
});
