import { describe, expect, it } from 'vitest';
import type { DiagramDocument } from '@/features/diagram-editor/model/diagramDocument';
import {
  assertValidDiagramDocument,
  validateDiagramDocument,
} from '@/features/diagram-editor/model/diagramValidation';

const validDocument: DiagramDocument = {
  schemaVersion: 1,
  nodes: [
    {
      id: 'source',
      type: 'hydraulic',
      position: { x: 0, y: 0 },
      data: { type: 'water-connection', label: 'Source', rotation: 0 },
    },
    {
      id: 'valve',
      type: 'hydraulic',
      position: { x: 100, y: 0 },
      data: { type: 'ball-valve', label: 'Valve', rotation: 0 },
    },
  ],
  edges: [
    {
      id: 'edge-1',
      source: 'source',
      sourceHandle: 'outlet',
      target: 'valve',
      targetHandle: 'inlet',
      type: 'hydraulic',
      data: { lineType: 'pipe_cold_water' },
    },
  ],
};

describe('diagramValidation', () => {
  it('accepts a valid diagram document', () => {
    expect(validateDiagramDocument(validDocument)).toEqual([]);
    expect(() => assertValidDiagramDocument(validDocument)).not.toThrow();
  });

  it('rejects unknown element types and non-cardinal rotation', () => {
    const document: DiagramDocument = {
      ...validDocument,
      nodes: [
        {
          ...validDocument.nodes[0],
          data: { type: 'unknown', label: 'Unknown', rotation: 45 },
        },
      ],
      edges: [],
    };

    expect(validateDiagramDocument(document)).toEqual([
      'Node "source" references unknown element type "unknown".',
      'Node "source" has unsupported rotation "45".',
    ]);
  });

  it('rejects edges that reference missing nodes, ports or line types', () => {
    const document: DiagramDocument = {
      ...validDocument,
      edges: [
        {
          ...validDocument.edges[0],
          source: 'missing',
          targetHandle: 'missing-port',
          data: { lineType: 'pipe_unknown' },
        },
      ],
    };

    expect(validateDiagramDocument(document)).toEqual([
      'Edge "edge-1" references missing source node "missing".',
      'Edge "edge-1" references missing target port "missing-port".',
      'Edge "edge-1" references unknown line type "pipe_unknown".',
    ]);
  });

  it('rejects a line type disallowed by a port', () => {
    const document: DiagramDocument = {
      ...validDocument,
      edges: [
        {
          ...validDocument.edges[0],
          data: { lineType: 'pipe_hot_water' },
        },
      ],
    };

    expect(validateDiagramDocument(document)).toEqual([
      'Edge "edge-1" line type "pipe_hot_water" is not allowed by source port "outlet".',
    ]);
  });
});
