import type { Edge, Node, Viewport } from 'reactflow';
import type { HydraulicEdgeData, HydraulicNodeData } from './types';

export const CURRENT_SCHEMA_VERSION = 1;

export interface DiagramDocumentSettings {
  showGrid?: boolean;
  snapToGrid?: boolean;
  activeLineType?: string;
  showLabels?: boolean;
}

export interface DiagramDocument {
  schemaVersion: typeof CURRENT_SCHEMA_VERSION;
  nodes: Node<HydraulicNodeData>[];
  edges: Edge<HydraulicEdgeData>[];
  viewport?: Viewport;
  settings?: DiagramDocumentSettings;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isViewport(value: unknown): value is Viewport {
  return (
    isObject(value) &&
    typeof value.x === 'number' &&
    typeof value.y === 'number' &&
    typeof value.zoom === 'number'
  );
}

function isSettings(value: unknown): value is DiagramDocumentSettings {
  if (value === undefined) return true;
  if (!isObject(value)) return false;

  return (
    (value.showGrid === undefined || typeof value.showGrid === 'boolean') &&
    (value.snapToGrid === undefined || typeof value.snapToGrid === 'boolean') &&
    (value.activeLineType === undefined || typeof value.activeLineType === 'string') &&
    (value.showLabels === undefined || typeof value.showLabels === 'boolean')
  );
}

function hasId(value: unknown): value is { id: string } {
  return isObject(value) && typeof value.id === 'string';
}

export function isDiagramDocument(value: unknown): value is DiagramDocument {
  if (!isObject(value)) return false;

  return (
    value.schemaVersion === CURRENT_SCHEMA_VERSION &&
    Array.isArray(value.nodes) &&
    value.nodes.every(hasId) &&
    Array.isArray(value.edges) &&
    value.edges.every(hasId) &&
    (value.viewport === undefined || isViewport(value.viewport)) &&
    isSettings(value.settings)
  );
}

export function assertDiagramDocument(value: unknown): asserts value is DiagramDocument {
  if (!isDiagramDocument(value)) {
    throw new Error('Файл не похож на поддерживаемый JSON документ схемы.');
  }
}
