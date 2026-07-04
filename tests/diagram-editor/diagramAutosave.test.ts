import { describe, expect, it } from 'vitest';
import type { DiagramDocument } from '@/features/diagram-editor/model/diagramDocument';
import {
  decodeAutosaveDocument,
  encodeAutosaveDocument,
} from '@/features/diagram-editor/persistence';

const document: DiagramDocument = {
  schemaVersion: 1,
  nodes: [
    {
      id: 'pump-1',
      type: 'hydraulic',
      position: { x: 10, y: 20 },
      data: { type: 'pump', label: 'Насос', rotation: 0 },
    },
  ],
  edges: [],
  settings: {
    showGrid: true,
    snapToGrid: false,
    activeLineType: 'pipe_cold_water',
  },
};

describe('diagramAutosave', () => {
  it('round-trips a valid diagram document', () => {
    expect(decodeAutosaveDocument(encodeAutosaveDocument(document))).toEqual(document);
  });

  it('rejects invalid autosave data before restore', () => {
    const invalid = JSON.stringify({
      ...document,
      nodes: [
        {
          ...document.nodes[0],
          data: { type: 'missing-element', label: 'Broken' },
        },
      ],
    });

    expect(() => decodeAutosaveDocument(invalid)).toThrow('Файл схемы содержит ошибки');
  });
});
