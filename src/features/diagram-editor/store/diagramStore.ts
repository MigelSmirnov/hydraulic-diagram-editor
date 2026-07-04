import { create } from 'zustand';
import {
  applyNodeChanges,
  applyEdgeChanges,
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
import { DEFAULT_LINE_TYPE } from '../model/lineTypes';
import { getTemplate } from '../model/templates';
import {
  addElementCommand,
  clearDiagramCommand,
  connectPorts,
  deleteEdgeCommand,
  deleteNodeCommand,
  loadTemplateCommand,
  replaceDiagramCommand,
  resolveLineTypeCommand,
  rotateNodeCommand,
  updateEdgeLineTypeCommand,
  updateNodeLineTypeCommand,
} from './diagramCommands';
import {
  pushDiagramHistory,
  redoDiagramHistory,
  undoDiagramHistory,
  type DiagramHistoryState,
} from './diagramHistory';

export type HNode = Node<HydraulicNodeData>;
export type HEdge = Edge<HydraulicEdgeData>;

interface DiagramState {
  // --- data ---
  nodes: HNode[];
  edges: HEdge[];
  past: DiagramHistoryState['past'];
  future: DiagramHistoryState['future'];

  // --- editor settings ---
  selectedLineType: LineTypeId;
  lastElementType?: string;
  showGrid: boolean;
  snapToGrid: boolean;

  // --- panel visibility (UI chrome, not persisted in the diagram) ---
  showPalette: boolean;
  showProperties: boolean;

  // --- React Flow bindings ---
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  commitHistoryCheckpoint: () => void;

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
  updateNodeLineType: (nodeId: string, lineType: LineTypeId) => void;
  rotateNode: (nodeId: string) => void;
  deleteNode: (nodeId: string) => void;
  deleteEdge: (edgeId: string) => void;
  undo: () => void;
  redo: () => void;
  toggleGrid: () => void;
  toggleSnap: () => void;
  togglePalette: () => void;
  toggleProperties: () => void;
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
  past: [],
  future: [],
  selectedLineType: DEFAULT_LINE_TYPE,
  lastElementType: undefined,
  showGrid: false,
  snapToGrid: false,
  showPalette: true,
  showProperties: true,

  onNodesChange: (changes) =>
    set({ nodes: applyNodeChanges(changes, get().nodes) as HNode[] }),

  onEdgesChange: (changes) =>
    set({ edges: applyEdgeChanges(changes, get().edges) as HEdge[] }),

  onConnect: (connection) =>
    set((state) => {
      const nextEdges = connectPorts(state.edges, connection, state.selectedLineType);
      return {
        ...pushDiagramHistory(state, state),
        edges: nextEdges,
      };
    }),

  commitHistoryCheckpoint: () =>
    set((state) => pushDiagramHistory(state, state)),

  addElement: (type, position) =>
    set((state) => {
      const nextNodes = addElementCommand(state.nodes, type, position, state.selectedLineType);
      return {
        ...pushDiagramHistory(state, state),
        nodes: nextNodes,
        lastElementType: type,
      };
    }),

  clear: () =>
    set((state) => ({
      ...pushDiagramHistory(state, state),
      ...clearDiagramCommand(),
    })),

  loadTemplate: (id) => {
    const template = getTemplate(id);
    if (!template) return;

    set((state) => ({
      ...pushDiagramHistory(state, state),
      ...loadTemplateCommand(template),
    }));
  },

  replaceDiagram: ({ nodes, edges, settings }) =>
    set((state) =>
      ({
        ...pushDiagramHistory(state, state),
        ...replaceDiagramCommand(
          {
            selectedLineType: state.selectedLineType,
            showGrid: state.showGrid,
            snapToGrid: state.snapToGrid,
          },
          { nodes, edges, settings },
        ),
      }),
    ),

  setLineType: (id) => set({ selectedLineType: resolveLineTypeCommand(id) }),
  updateEdgeLineType: (edgeId, lineType) =>
    set((state) => ({
      ...pushDiagramHistory(state, state),
      edges: updateEdgeLineTypeCommand(state.edges, edgeId, lineType),
    })),
  updateNodeLineType: (nodeId, lineType) =>
    set((state) => ({
      ...pushDiagramHistory(state, state),
      nodes: updateNodeLineTypeCommand(state.nodes, nodeId, lineType),
    })),
  rotateNode: (nodeId) =>
    set((state) => ({
      ...pushDiagramHistory(state, state),
      nodes: rotateNodeCommand(state.nodes, nodeId),
    })),
  deleteNode: (nodeId) =>
    set((state) => ({
      ...pushDiagramHistory(state, state),
      ...deleteNodeCommand(state.nodes, state.edges, nodeId),
    })),
  deleteEdge: (edgeId) =>
    set((state) => ({
      ...pushDiagramHistory(state, state),
      edges: deleteEdgeCommand(state.edges, edgeId),
    })),
  undo: () =>
    set((state) =>
      undoDiagramHistory(state, state) ?? {},
    ),
  redo: () =>
    set((state) =>
      redoDiagramHistory(state, state) ?? {},
    ),
  toggleGrid: () => set((s) => ({ showGrid: !s.showGrid })),
  toggleSnap: () => set((s) => ({ snapToGrid: !s.snapToGrid })),
  togglePalette: () => set((s) => ({ showPalette: !s.showPalette })),
  toggleProperties: () => set((s) => ({ showProperties: !s.showProperties })),
}));
