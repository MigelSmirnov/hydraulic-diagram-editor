import { describe, expect, it } from 'vitest';
import {
  getRotatedPortDirection,
  getRotatedPortPosition,
  getRotatedSymbolSize,
  normalizeRotation,
} from '@/features/diagram-editor/utils/portGeometry';

describe('portGeometry', () => {
  it('normalizes arbitrary rotations to supported cardinal values', () => {
    expect(normalizeRotation()).toBe(0);
    expect(normalizeRotation(90)).toBe(90);
    expect(normalizeRotation(450)).toBe(90);
    expect(normalizeRotation(-90)).toBe(270);
    expect(normalizeRotation(45)).toBe(0);
  });

  it('swaps symbol dimensions for quarter turns', () => {
    expect(getRotatedSymbolSize(80, 40, 0)).toEqual({ width: 80, height: 40 });
    expect(getRotatedSymbolSize(80, 40, 90)).toEqual({ width: 40, height: 80 });
    expect(getRotatedSymbolSize(80, 40, 270)).toEqual({ width: 40, height: 80 });
  });

  it('rotates port coordinates inside symbol bounds', () => {
    expect(getRotatedPortPosition({ x: 0, y: 20 }, 80, 40, 90)).toEqual({ x: 20, y: 0 });
    expect(getRotatedPortPosition({ x: 80, y: 20 }, 80, 40, 180)).toEqual({ x: 0, y: 20 });
    expect(getRotatedPortPosition({ x: 40, y: 0 }, 80, 40, 270)).toEqual({ x: 0, y: 40 });
  });

  it('rotates port directions with the symbol', () => {
    expect(getRotatedPortDirection('left', 90)).toBe('top');
    expect(getRotatedPortDirection('bottom', 180)).toBe('top');
    expect(getRotatedPortDirection('right', 270)).toBe('top');
  });
});
