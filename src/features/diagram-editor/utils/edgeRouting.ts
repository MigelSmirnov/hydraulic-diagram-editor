import type { PortDirection } from '../model/types';
import type { Point } from './portGeometry';

export interface OrthogonalRouteOptions {
  stubLength?: number;
}

export function directionToVector(direction: PortDirection): Point {
  if (direction === 'left') return { x: -1, y: 0 };
  if (direction === 'right') return { x: 1, y: 0 };
  if (direction === 'top') return { x: 0, y: -1 };
  return { x: 0, y: 1 };
}

export function getStubPoint(
  point: Point,
  direction: PortDirection,
  length: number,
): Point {
  const vector = directionToVector(direction);
  return {
    x: point.x + vector.x * length,
    y: point.y + vector.y * length,
  };
}

function pointsEqual(a: Point, b: Point): boolean {
  return a.x === b.x && a.y === b.y;
}

function compactPoints(points: Point[]): Point[] {
  return points.filter((point, index) => index === 0 || !pointsEqual(point, points[index - 1]));
}

export function buildOrthogonalPath(
  sourcePoint: Point,
  sourceDirection: PortDirection,
  targetPoint: Point,
  targetDirection: PortDirection,
  options: OrthogonalRouteOptions = {},
): string {
  const stubLength = options.stubLength ?? 16;
  const sourceStub = getStubPoint(sourcePoint, sourceDirection, stubLength);
  const targetStub = getStubPoint(targetPoint, targetDirection, stubLength);
  const dx = Math.abs(targetStub.x - sourceStub.x);
  const dy = Math.abs(targetStub.y - sourceStub.y);
  const routePoints: Point[] = [sourcePoint, sourceStub];

  if (dx >= dy) {
    const midX = (sourceStub.x + targetStub.x) / 2;
    routePoints.push({ x: midX, y: sourceStub.y }, { x: midX, y: targetStub.y });
  } else {
    const midY = (sourceStub.y + targetStub.y) / 2;
    routePoints.push({ x: sourceStub.x, y: midY }, { x: targetStub.x, y: midY });
  }

  routePoints.push(targetStub, targetPoint);

  return compactPoints(routePoints)
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ');
}
