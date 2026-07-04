import { describe, expect, it } from 'vitest';
import type { DiagramData } from '@/features/diagram-editor/store/diagramCommands';
import {
  pushDiagramHistory,
  redoDiagramHistory,
  undoDiagramHistory,
} from '@/features/diagram-editor/store/diagramHistory';

const emptyDiagram: DiagramData = {
  nodes: [],
  edges: [],
};

const oneNodeDiagram: DiagramData = {
  nodes: [
    {
      id: 'node-1',
      type: 'hydraulic',
      position: { x: 0, y: 0 },
      data: { type: 'ball-valve', label: 'Valve', rotation: 0 },
    },
  ],
  edges: [],
};

const twoNodeDiagram: DiagramData = {
  nodes: [
    ...oneNodeDiagram.nodes,
    {
      id: 'node-2',
      type: 'hydraulic',
      position: { x: 100, y: 0 },
      data: { type: 'filter', label: 'Filter', rotation: 0 },
    },
  ],
  edges: [],
};

describe('diagramHistory', () => {
  it('pushes the current diagram into past and clears future', () => {
    expect(
      pushDiagramHistory(
        {
          past: [emptyDiagram],
          future: [twoNodeDiagram],
        },
        oneNodeDiagram,
      ),
    ).toEqual({
      past: [emptyDiagram, oneNodeDiagram],
      future: [],
    });
  });

  it('undoes to the previous diagram and moves current into future', () => {
    expect(
      undoDiagramHistory(
        {
          past: [emptyDiagram, oneNodeDiagram],
          future: [],
        },
        twoNodeDiagram,
      ),
    ).toEqual({
      nodes: oneNodeDiagram.nodes,
      edges: oneNodeDiagram.edges,
      past: [emptyDiagram],
      future: [twoNodeDiagram],
    });
  });

  it('redoes to the next diagram and moves current into past', () => {
    expect(
      redoDiagramHistory(
        {
          past: [emptyDiagram],
          future: [twoNodeDiagram],
        },
        oneNodeDiagram,
      ),
    ).toEqual({
      nodes: twoNodeDiagram.nodes,
      edges: twoNodeDiagram.edges,
      past: [emptyDiagram, oneNodeDiagram],
      future: [],
    });
  });

  it('returns undefined when undo or redo is unavailable', () => {
    expect(undoDiagramHistory({ past: [], future: [] }, emptyDiagram)).toBeUndefined();
    expect(redoDiagramHistory({ past: [], future: [] }, emptyDiagram)).toBeUndefined();
  });
});
