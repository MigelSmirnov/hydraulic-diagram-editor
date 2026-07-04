import type { Edge, Node, Viewport } from 'reactflow';
import {
  assertDiagramDocument,
  CURRENT_SCHEMA_VERSION,
  type DiagramDocument,
  type DiagramDocumentSettings,
} from '../model/diagramDocument';
import { assertValidDiagramDocument } from '../model/diagramValidation';
import type { HydraulicEdgeData, HydraulicNodeData } from '../model/types';

interface SerializeDiagramInput {
  nodes: Node<HydraulicNodeData>[];
  edges: Edge<HydraulicEdgeData>[];
  viewport?: Viewport;
  settings?: DiagramDocumentSettings;
}

export function serializeDiagram({
  nodes,
  edges,
  viewport,
  settings,
}: SerializeDiagramInput): DiagramDocument {
  return {
    schemaVersion: CURRENT_SCHEMA_VERSION,
    nodes,
    edges,
    viewport,
    settings,
  };
}

export function deserializeDiagram(value: unknown): DiagramDocument {
  assertDiagramDocument(value);
  assertValidDiagramDocument(value);
  return value;
}

export function downloadDiagramJson(
  document: DiagramDocument,
  filename = 'hydraulic-diagram.json',
): void {
  const blob = new Blob([JSON.stringify(document, null, 2)], {
    type: 'application/json;charset=utf-8',
  });
  const url = URL.createObjectURL(blob);
  const link = window.document.createElement('a');

  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function readDiagramJsonFile(file: File): Promise<unknown> {
  return file.text().then((text) => {
    try {
      return JSON.parse(text) as unknown;
    } catch {
      throw new Error('Файл не удалось прочитать как корректный JSON.');
    }
  });
}
