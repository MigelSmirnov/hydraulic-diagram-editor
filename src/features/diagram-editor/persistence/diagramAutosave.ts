import type { DiagramDocument } from '../model/diagramDocument';
import { deserializeDiagram } from './diagramJson';

export const DIAGRAM_AUTOSAVE_KEY = 'hydraulic-diagram-editor.autosave.v1';

export function encodeAutosaveDocument(document: DiagramDocument): string {
  return JSON.stringify(document);
}

export function decodeAutosaveDocument(value: string): DiagramDocument {
  return deserializeDiagram(JSON.parse(value) as unknown);
}

export function saveAutosaveDocument(storage: Storage, document: DiagramDocument): void {
  storage.setItem(DIAGRAM_AUTOSAVE_KEY, encodeAutosaveDocument(document));
}

export function loadAutosaveDocument(storage: Storage): DiagramDocument | undefined {
  const raw = storage.getItem(DIAGRAM_AUTOSAVE_KEY);
  if (!raw) return undefined;

  return decodeAutosaveDocument(raw);
}

export function clearAutosaveDocument(storage: Storage): void {
  storage.removeItem(DIAGRAM_AUTOSAVE_KEY);
}
