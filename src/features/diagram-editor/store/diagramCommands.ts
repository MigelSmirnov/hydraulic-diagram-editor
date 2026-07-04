import {
  addEdge,
  type Connection,
  type Edge,
  type Node,
} from 'reactflow';
import { DEFAULT_LINE_TYPE, isLineTypeId } from '../model/lineTypes';
import type { DiagramDocumentSettings } from '../model/diagramDocument';
import type {
  DiagramTemplate,
  HydraulicEdgeData,
  HydraulicNodeData,
  LineTypeId,
} from '../model/types';
import { createNode } from '../utils/createNode';

export type HNode = Node<HydraulicNodeData>;
export type HEdge = Edge<HydraulicEdgeData>;

export interface DiagramData {
  nodes: HNode[];
  edges: HEdge[];
}

export interface DiagramSettingsState {
  selectedLineType: LineTypeId;
  showGrid: boolean;
  snapToGrid: boolean;
}

export function connectPorts(
  edges: HEdge[],
  connection: Connection,
  selectedLineType: LineTypeId,
): HEdge[] {
  return addEdge(
    {
      ...connection,
      type: 'hydraulic',
      data: { lineType: selectedLineType },
    },
    edges,
  ) as HEdge[];
}

export function addElementCommand(
  nodes: HNode[],
  type: string,
  position: { x: number; y: number },
  selectedLineType: LineTypeId,
): HNode[] {
  const node = createNode(type, position);
  return [
    ...nodes,
    {
      ...node,
      data: {
        ...node.data,
        lineType: selectedLineType,
      },
    },
  ];
}

export function clearDiagramCommand(): DiagramData {
  return { nodes: [], edges: [] };
}

export function loadTemplateCommand(template: DiagramTemplate): DiagramData {
  const nodes = template.nodes.map((node) =>
    createNode(node.type, node.position, node.id, node.label),
  );

  const edges: HEdge[] = template.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    sourceHandle: edge.sourceHandle,
    target: edge.target,
    targetHandle: edge.targetHandle,
    type: 'hydraulic',
    data: { lineType: edge.lineType },
  }));

  return { nodes, edges };
}

export function replaceDiagramCommand(
  currentSettings: DiagramSettingsState,
  input: DiagramData & { settings?: DiagramDocumentSettings },
): DiagramData & DiagramSettingsState {
  return {
    nodes: input.nodes,
    edges: input.edges,
    showGrid: input.settings?.showGrid ?? currentSettings.showGrid,
    snapToGrid: input.settings?.snapToGrid ?? currentSettings.snapToGrid,
    selectedLineType: input.settings?.activeLineType
      ? input.settings.activeLineType
      : currentSettings.selectedLineType,
  };
}

export function resolveLineTypeCommand(id: LineTypeId): LineTypeId {
  return isLineTypeId(id) ? id : DEFAULT_LINE_TYPE;
}

export function updateEdgeLineTypeCommand(
  edges: HEdge[],
  edgeId: string,
  lineType: LineTypeId,
): HEdge[] {
  return edges.map((edge) =>
    edge.id === edgeId
      ? { ...edge, data: { ...edge.data, lineType } }
      : edge,
  );
}

export function updateNodeLineTypeCommand(
  nodes: HNode[],
  nodeId: string,
  lineType: LineTypeId,
): HNode[] {
  return nodes.map((node) =>
    node.id === nodeId
      ? { ...node, data: { ...node.data, lineType } }
      : node,
  );
}

export function rotateNodeCommand(nodes: HNode[], nodeId: string): HNode[] {
  return nodes.map((node) =>
    node.id === nodeId
      ? {
          ...node,
          data: {
            ...node.data,
            rotation: ((node.data.rotation ?? 0) + 90) % 360,
          },
        }
      : node,
  );
}

export function deleteNodeCommand(
  nodes: HNode[],
  edges: HEdge[],
  nodeId: string,
): DiagramData {
  return {
    nodes: nodes.filter((node) => node.id !== nodeId),
    edges: edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
  };
}

export function deleteEdgeCommand(edges: HEdge[], edgeId: string): HEdge[] {
  return edges.filter((edge) => edge.id !== edgeId);
}
