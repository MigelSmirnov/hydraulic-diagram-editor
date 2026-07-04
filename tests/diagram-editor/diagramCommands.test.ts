import { describe, expect, it } from 'vitest';
import type { Connection } from 'reactflow';
import { STARTER_TEMPLATE_ID, getTemplate } from '@/features/diagram-editor/model/templates';
import {
  connectPorts,
  deleteEdgeCommand,
  deleteNodeCommand,
  loadTemplateCommand,
  replaceDiagramCommand,
  resolveLineTypeCommand,
  rotateNodeCommand,
  updateEdgeLineTypeCommand,
  updateNodeLineTypeCommand,
  type HEdge,
  type HNode,
} from '@/features/diagram-editor/store/diagramCommands';

const nodes: HNode[] = [
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
    data: { type: 'ball-valve', label: 'Valve', rotation: 270 },
  },
];

const edges: HEdge[] = [
  {
    id: 'edge-1',
    source: 'source',
    sourceHandle: 'outlet',
    target: 'valve',
    targetHandle: 'inlet',
    type: 'hydraulic',
    data: { lineType: 'pipe_cold_water' },
  },
  {
    id: 'edge-2',
    source: 'valve',
    sourceHandle: 'outlet',
    target: 'target',
    targetHandle: 'inlet',
    type: 'hydraulic',
    data: { lineType: 'pipe_cold_water' },
  },
];

describe('diagramCommands', () => {
  it('connects ports with the selected line type', () => {
    const connection: Connection = {
      source: 'source',
      sourceHandle: 'outlet',
      target: 'valve',
      targetHandle: 'inlet',
    };

    const result = connectPorts([], connection, 'pipe_hot_water');

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      source: 'source',
      sourceHandle: 'outlet',
      target: 'valve',
      targetHandle: 'inlet',
      type: 'hydraulic',
      data: { lineType: 'pipe_hot_water' },
    });
  });

  it('rotates a node by one cardinal step', () => {
    expect(rotateNodeCommand(nodes, 'valve').find((node) => node.id === 'valve')?.data.rotation).toBe(0);
    expect(rotateNodeCommand(nodes, 'source').find((node) => node.id === 'source')?.data.rotation).toBe(90);
  });

  it('deletes a node and its connected edges', () => {
    expect(deleteNodeCommand(nodes, edges, 'source')).toEqual({
      nodes: [nodes[1]],
      edges: [edges[1]],
    });
  });

  it('deletes one edge without changing nodes', () => {
    expect(deleteEdgeCommand(edges, 'edge-1')).toEqual([edges[1]]);
  });

  it('updates node and edge line types by id', () => {
    expect(updateNodeLineTypeCommand(nodes, 'source', 'pipe_hot_water')[0].data.lineType).toBe('pipe_hot_water');
    expect(updateEdgeLineTypeCommand(edges, 'edge-1', 'pipe_hot_water')[0].data?.lineType).toBe('pipe_hot_water');
  });

  it('falls back to the default line type for unknown ids', () => {
    expect(resolveLineTypeCommand('missing')).toBe('pipe_cold_water');
    expect(resolveLineTypeCommand('pipe_hot_water')).toBe('pipe_hot_water');
  });

  it('loads template nodes and edges into editable canvas structures', () => {
    const template = getTemplate(STARTER_TEMPLATE_ID);
    if (!template) throw new Error('Starter template is missing.');

    const result = loadTemplateCommand(template);

    expect(result.nodes).toHaveLength(template.nodes.length);
    expect(result.edges).toHaveLength(template.edges.length);
    expect(result.nodes[0]).toMatchObject({
      id: template.nodes[0].id,
      type: 'hydraulic',
      data: { type: template.nodes[0].type },
    });
  });

  it('replaces diagram data while preserving settings not present in the document', () => {
    expect(
      replaceDiagramCommand(
        {
          selectedLineType: 'pipe_hot_water',
          showGrid: true,
          snapToGrid: false,
        },
        {
          nodes,
          edges,
          settings: { snapToGrid: true },
        },
      ),
    ).toEqual({
      nodes,
      edges,
      selectedLineType: 'pipe_hot_water',
      showGrid: true,
      snapToGrid: true,
    });
  });
});
