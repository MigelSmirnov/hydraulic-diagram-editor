import { useEffect } from 'react';
import {
  loadAutosaveDocument,
  saveAutosaveDocument,
  serializeDiagram,
} from '../persistence';
import { useDiagramStore } from '../store/diagramStore';

const AUTOSAVE_DEBOUNCE_MS = 250;

export function DiagramAutosave() {
  useEffect(() => {
    const state = useDiagramStore.getState();

    try {
      const document = loadAutosaveDocument(window.localStorage);
      if (document) {
        state.restoreDiagram({
          nodes: document.nodes,
          edges: document.edges,
          settings: document.settings,
        });
      }
    } catch (error) {
      console.warn('Diagram autosave restore failed:', error);
    }

    let timeoutId: number | undefined;
    const unsubscribe = useDiagramStore.subscribe((nextState) => {
      window.clearTimeout(timeoutId);
      timeoutId = window.setTimeout(() => {
        const document = serializeDiagram({
          nodes: nextState.nodes,
          edges: nextState.edges,
          settings: {
            showGrid: nextState.showGrid,
            snapToGrid: nextState.snapToGrid,
            activeLineType: nextState.selectedLineType,
          },
        });

        saveAutosaveDocument(window.localStorage, document);
      }, AUTOSAVE_DEBOUNCE_MS);
    });

    return () => {
      window.clearTimeout(timeoutId);
      unsubscribe();
    };
  }, []);

  return null;
}
