import { create } from 'zustand';
import {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  type Connection,
  type NodeChange,
  type EdgeChange,
} from 'reactflow';
import type {
  HydraulicNodeData,
  HydraulicEdgeData,
  LineTypeId,
} from '../model/types';
import type { DiagramDocumentSettings } from '../model/diagramDocument';
import { DEFAULT_LINE_TYPE, isLineTypeId } from '../model/lineTypes';
import { createNode } from '../utils/createNode';
import { getTemplate } from '../model/templates';

export type HNode = Node<HydraulicNodeData>;
export type HEdge = Edge<HydraulicEdgeData>;

interface DiagramState {
  // --- data ---
  nodes: HNode[];
  edges: HEdge[];

  // --- editor settings ---
  selectedLineType: LineTypeId;
  showGrid: boolean;
  snapToGrid: boolean;

  // --- React Flow bindings ---
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;

  // --- actions ---
  addElement: (type: string, position: { x: number; y: number }) => void;
  clear: () => void;
  loadTemplate: (id: string) => void;
  replaceDiagram: (input: {
    nodes: HNode[];
    edges: HEdge[];
    settings?: DiagramDocumentSettings;
  }) => void;
  setLineType: (id: LineTypeId) => void;
  updateEdgeLineType: (edgeId: string, lineType: LineTypeId) => void;
  rotateNode: (nodeId: string) => void;
  deleteNode: (nodeId: string) => void;
  deleteEdge: (edgeId: string) => void;
  toggleGrid: () => void;
  toggleSnap: () => void;
}

/**
 * Central editor store. Every component reads and mutates diagram state
 * through here — never via prop drilling. Selection lives on the nodes/edges
 * themselves (React Flow's `selected` flag), so the properties panel just
 * looks for the selected item.
 */
export const useDiagramStore = create<DiagramState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedLineType: DEFAULT_LINE_TYPE,
  showGrid: false,
  snapToGrid: false,

  onNodesChange: (changes) =>
    set({ nodes: applyNodeChanges(changes, get().nodes) as HNode[] }),

  onEdgesChange: (changes) =>
    set({ edges: applyEdgeChanges(changes, get().edges) as HEdge[] }),

  onConnect: (connection) =>
    set({
      edges: addEdge(
        {
          ...connection,
          type: 'hydraulic',
          data: { lineType: get().selectedLineType },
        },
        get().edges,
      ) as HEdge[],
    }),

  addElement: (type, position) =>
    set({ nodes: [...get().nodes, createNode(type, position)] }),

  clear: () => set({ nodes: [], edges: [] }),

  loadTemplate: (id) => {
    const template = getTemplate(id);
    if (!template) return;

    const nodes = template.nodes.map((n) =>
      createNode(n.type, n.position, n.id, n.label),
    );

    const edges: HEdge[] = template.edges.map((e) => ({
      id: e.id,
      source: e.source,
      sourceHandle: e.sourceHandle,
      target: e.target,
      targetHandle: e.targetHandle,
      type: 'hydraulic',
      data: { lineType: e.lineType },
    }));

    set({ nodes, edges });
  },

  replaceDiagram: ({ nodes, edges, settings }) =>
    set((state) => ({
      nodes,
      edges,
      showGrid: settings?.showGrid ?? state.showGrid,
      snapToGrid: settings?.snapToGrid ?? state.snapToGrid,
      selectedLineType: settings?.activeLineType
        ? settings.activeLineType
        : state.selectedLineType,
    })),

  setLineType: (id) => set({ selectedLineType: isLineTypeId(id) ? id : DEFAULT_LINE_TYPE }),
  updateEdgeLineType: (edgeId, lineType) =>
    set({
      edges: get().edges.map((edge) =>
        edge.id === edgeId
          ? { ...edge, data: { ...edge.data, lineType } }
          : edge,
      ),
    }),
  rotateNode: (nodeId) =>
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: {
                ...node.data,
                rotation: ((node.data.rotation ?? 0) + 90) % 360,
              },
            }
          : node,
      ),
    }),
  deleteNode: (nodeId) =>
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
    }),
  deleteEdge: (edgeId) =>
    set({ edges: get().edges.filter((edge) => edge.id !== edgeId) }),
  toggleGrid: () => set((s) => ({ showGrid: !s.showGrid })),
  toggleSnap: () => set((s) => ({ snapToGrid: !s.snapToGrid })),
}));
