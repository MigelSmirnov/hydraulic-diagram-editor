import type { ElementSize, PortDirection } from '../model/types';

export type CardinalRotation = 0 | 90 | 180 | 270;

export interface Point {
  x: number;
  y: number;
}

export function normalizeRotation(rotation?: number): CardinalRotation {
  const normalized = (((rotation ?? 0) % 360) + 360) % 360;
  if (normalized === 90 || normalized === 180 || normalized === 270) return normalized;
  return 0;
}

export function getRotatedSymbolSize(
  width: number,
  height: number,
  rotation?: number,
): ElementSize {
  const normalized = normalizeRotation(rotation);
  if (normalized === 90 || normalized === 270) {
    return { width: height, height: width };
  }

  return { width, height };
}

export function getRotatedPortPosition(
  point: Point,
  width: number,
  height: number,
  rotation?: number,
): Point {
  const normalized = normalizeRotation(rotation);

  if (normalized === 90) return { x: height - point.y, y: point.x };
  if (normalized === 180) return { x: width - point.x, y: height - point.y };
  if (normalized === 270) return { x: point.y, y: width - point.x };

  return point;
}

const DIRECTION_ROTATION: PortDirection[] = ['top', 'right', 'bottom', 'left'];

export function getRotatedPortDirection(
  direction: PortDirection,
  rotation?: number,
): PortDirection {
  const offset = normalizeRotation(rotation) / 90;
  const index = DIRECTION_ROTATION.indexOf(direction);
  return DIRECTION_ROTATION[(index + offset) % DIRECTION_ROTATION.length];
}
