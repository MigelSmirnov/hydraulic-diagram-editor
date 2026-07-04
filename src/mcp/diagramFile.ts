import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import type { Edge, Node } from 'reactflow';
import { CURRENT_SCHEMA_VERSION, type DiagramDocument } from '../features/diagram-editor/model/diagramDocument';
import { assertValidDiagramDocument, validateDiagramDocument } from '../features/diagram-editor/model/diagramValidation';
import { getElementDef } from '../features/diagram-editor/model/elementCatalog';
import { DEFAULT_LINE_TYPE, isLineTypeId } from '../features/diagram-editor/model/lineTypes';
import type { HydraulicEdgeData, HydraulicNodeData } from '../features/diagram-editor/model/types';
import { createId } from '../lib/id';

const DEFAULT_DIAGRAM_FILE = 'hydraulic-diagram.agent.json';

export interface DiagramPathInput {
  diagramPath?: string;
}

export interface AddElementInput extends DiagramPathInput {
  type: string;
  x: number;
  y: number;
  id?: string;
  label?: string;
  rotation?: 0 | 90 | 180 | 270;
  lineType?: string;
}

export interface UpdateElementInput extends DiagramPathInput {
  nodeId: string;
  x?: number;
  y?: number;
  label?: string;
  rotation?: 0 | 90 | 180 | 270;
  lineType?: string;
}

export interface ConnectPortsInput extends DiagramPathInput {
  sourceId: string;
  sourcePortId: string;
  targetId: string;
  targetPortId: string;
  lineType?: string;
  id?: string;
}

export interface DiagramMutationResult {
  diagramPath: string;
  document: DiagramDocument;
}

function emptyDiagram(): DiagramDocument {
  return {
    schemaVersion: CURRENT_SCHEMA_VERSION,
    nodes: [],
    edges: [],
    settings: {
      activeLineType: DEFAULT_LINE_TYPE,
    },
  };
}

export function resolveDiagramPath(inputPath?: string): string {
  const requestedPath = inputPath ?? process.env.HYDRAULIC_DIAGRAM_FILE ?? DEFAULT_DIAGRAM_FILE;
  const resolvedPath = path.resolve(process.cwd(), requestedPath);
  const projectRoot = `${process.cwd()}${path.sep}`;

  if (resolvedPath !== process.cwd() && !resolvedPath.startsWith(projectRoot)) {
    throw new Error(`Diagram path must stay inside project root: ${requestedPath}`);
  }

  return resolvedPath;
}

async function writeDiagramDocument(diagramPath: string, document: DiagramDocument): Promise<void> {
  assertValidDiagramDocument(document);
  await mkdir(path.dirname(diagramPath), { recursive: true });
  await writeFile(diagramPath, `${JSON.stringify(document, null, 2)}\n`, 'utf8');
}

export async function createDiagramFile(
  input: DiagramPathInput & { overwrite?: boolean } = {},
): Promise<DiagramMutationResult> {
  const diagramPath = resolveDiagramPath(input.diagramPath);
  if (!input.overwrite && existsSync(diagramPath)) {
    throw new Error(`Diagram already exists: ${diagramPath}`);
  }

  const document = emptyDiagram();
  await writeDiagramDocument(diagramPath, document);
  return { diagramPath, document };
}

export async function readDiagramFile(input: DiagramPathInput = {}): Promise<DiagramMutationResult> {
  const diagramPath = resolveDiagramPath(input.diagramPath);
  const text = await readFile(diagramPath, 'utf8');
  const document = JSON.parse(text) as DiagramDocument;
  assertValidDiagramDocument(document);
  return { diagramPath, document };
}

async function readDiagramFileOrEmpty(input: DiagramPathInput = {}): Promise<DiagramMutationResult> {
  const diagramPath = resolveDiagramPath(input.diagramPath);
  if (!existsSync(diagramPath)) {
    return { diagramPath, document: emptyDiagram() };
  }

  return readDiagramFile(input);
}

export async function addElementToDiagram(input: AddElementInput): Promise<DiagramMutationResult & { node: Node<HydraulicNodeData> }> {
  const def = getElementDef(input.type);
  if (!def) {
    throw new Error(`Unknown element type: ${input.type}`);
  }

  if (input.lineType !== undefined && !isLineTypeId(input.lineType)) {
    throw new Error(`Unknown line type: ${input.lineType}`);
  }

  const { diagramPath, document } = await readDiagramFileOrEmpty(input);
  const node: Node<HydraulicNodeData> = {
    id: input.id ?? createId(input.type),
    type: 'hydraulic',
    position: { x: input.x, y: input.y },
    data: {
      type: def.type,
      label: input.label ?? def.label,
      rotation: input.rotation ?? 0,
      lineType: input.lineType,
    },
  };

  const nextDocument = {
    ...document,
    nodes: [...document.nodes, node],
  };

  await writeDiagramDocument(diagramPath, nextDocument);
  return { diagramPath, document: nextDocument, node };
}

function getNode(document: DiagramDocument, nodeId: string): Node<HydraulicNodeData> {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    throw new Error(`Unknown node id: ${nodeId}`);
  }

  return node;
}

export async function updateElementInDiagram(
  input: UpdateElementInput,
): Promise<DiagramMutationResult & { node: Node<HydraulicNodeData> }> {
  if (input.lineType !== undefined && !isLineTypeId(input.lineType)) {
    throw new Error(`Unknown line type: ${input.lineType}`);
  }

  const { diagramPath, document } = await readDiagramFile(input);
  const currentNode = getNode(document, input.nodeId);
  const nextNode: Node<HydraulicNodeData> = {
    ...currentNode,
    position: {
      x: input.x ?? currentNode.position.x,
      y: input.y ?? currentNode.position.y,
    },
    data: {
      ...currentNode.data,
      label: input.label ?? currentNode.data.label,
      rotation: input.rotation ?? currentNode.data.rotation,
      lineType: input.lineType ?? currentNode.data.lineType,
    },
  };

  const nextDocument = {
    ...document,
    nodes: document.nodes.map((node) => (node.id === input.nodeId ? nextNode : node)),
  };

  await writeDiagramDocument(diagramPath, nextDocument);
  return { diagramPath, document: nextDocument, node: nextNode };
}

function assertPortExists(node: Node<HydraulicNodeData>, portId: string): void {
  const def = getElementDef(node.data.type);
  const port = def?.ports.find((candidate) => candidate.id === portId);
  if (!port) {
    throw new Error(`Node "${node.id}" does not have port "${portId}".`);
  }
}

export async function connectPortsInDiagram(
  input: ConnectPortsInput,
): Promise<DiagramMutationResult & { edge: Edge<HydraulicEdgeData> }> {
  const lineType = input.lineType ?? DEFAULT_LINE_TYPE;
  if (!isLineTypeId(lineType)) {
    throw new Error(`Unknown line type: ${lineType}`);
  }

  const { diagramPath, document } = await readDiagramFile(input);
  const sourceNode = getNode(document, input.sourceId);
  const targetNode = getNode(document, input.targetId);
  assertPortExists(sourceNode, input.sourcePortId);
  assertPortExists(targetNode, input.targetPortId);

  const edge: Edge<HydraulicEdgeData> = {
    id: input.id ?? createId('edge'),
    source: input.sourceId,
    sourceHandle: input.sourcePortId,
    target: input.targetId,
    targetHandle: input.targetPortId,
    type: 'hydraulic',
    data: { lineType },
  };
  const nextDocument = {
    ...document,
    edges: [...document.edges, edge],
  };

  await writeDiagramDocument(diagramPath, nextDocument);
  return { diagramPath, document: nextDocument, edge };
}

export async function validateDiagramFile(input: DiagramPathInput = {}): Promise<{ diagramPath: string; errors: string[] }> {
  const { diagramPath, document } = await readDiagramFile(input);
  return {
    diagramPath,
    errors: validateDiagramDocument(document),
  };
}
