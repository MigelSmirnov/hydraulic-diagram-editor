import type { DiagramData } from './diagramCommands';

export interface DiagramHistoryState {
  past: DiagramData[];
  future: DiagramData[];
}

export interface UndoRedoResult extends DiagramHistoryState, DiagramData {}

export function createDiagramSnapshot(data: DiagramData): DiagramData {
  return {
    nodes: data.nodes,
    edges: data.edges,
  };
}

export function pushDiagramHistory(
  history: DiagramHistoryState,
  current: DiagramData,
): DiagramHistoryState {
  return {
    past: [...history.past, createDiagramSnapshot(current)],
    future: [],
  };
}

export function undoDiagramHistory(
  history: DiagramHistoryState,
  current: DiagramData,
): UndoRedoResult | undefined {
  const previous = history.past[history.past.length - 1];
  if (!previous) return undefined;

  return {
    ...previous,
    past: history.past.slice(0, -1),
    future: [createDiagramSnapshot(current), ...history.future],
  };
}

export function redoDiagramHistory(
  history: DiagramHistoryState,
  current: DiagramData,
): UndoRedoResult | undefined {
  const next = history.future[0];
  if (!next) return undefined;

  return {
    ...next,
    past: [...history.past, createDiagramSnapshot(current)],
    future: history.future.slice(1),
  };
}
