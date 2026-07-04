import { beforeEach, describe, expect, it } from 'vitest';
import type { NodeChange } from 'reactflow';
import { useDiagramStore, type HNode } from '@/features/diagram-editor/store/diagramStore';

const initialNode: HNode = {
  id: 'node-1',
  type: 'hydraulic',
  position: { x: 0, y: 0 },
  data: { type: 'ball-valve', label: 'Valve', rotation: 0 },
};

describe('diagramStore history integration', () => {
  beforeEach(() => {
    useDiagramStore.setState({
      nodes: [],
      edges: [],
      past: [],
      future: [],
      selectedLineType: 'pipe_cold_water',
      showGrid: false,
      snapToGrid: false,
      showPalette: true,
      showProperties: true,
    });
  });

  it('undoes and redoes a drag move from a history checkpoint', () => {
    useDiagramStore.setState({ nodes: [initialNode] });

    useDiagramStore.getState().commitHistoryCheckpoint();
    useDiagramStore.getState().onNodesChange([
      {
        id: 'node-1',
        type: 'position',
        position: { x: 80, y: 40 },
        dragging: false,
      } satisfies NodeChange,
    ]);

    expect(useDiagramStore.getState().nodes[0].position).toEqual({ x: 80, y: 40 });
    expect(useDiagramStore.getState().past).toHaveLength(1);

    useDiagramStore.getState().undo();
    expect(useDiagramStore.getState().nodes[0].position).toEqual({ x: 0, y: 0 });
    expect(useDiagramStore.getState().future).toHaveLength(1);

    useDiagramStore.getState().redo();
    expect(useDiagramStore.getState().nodes[0].position).toEqual({ x: 80, y: 40 });
  });
});
