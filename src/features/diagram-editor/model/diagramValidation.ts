import type { Edge, Node } from 'reactflow';
import { getElementDef } from './elementCatalog';
import { isLineTypeId } from './lineTypes';
import type { DiagramDocument } from './diagramDocument';
import type { HydraulicEdgeData, HydraulicNodeData } from './types';

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function isCardinalRotation(value: unknown): boolean {
  return value === undefined || value === 0 || value === 90 || value === 180 || value === 270;
}

function getNodePortIds(node: Node<HydraulicNodeData>): Set<string> {
  const def = getElementDef(node.data?.type);
  return new Set(def?.ports.map((port) => port.id) ?? []);
}

function validateNode(node: Node<HydraulicNodeData>, errors: string[]): void {
  if (!node.id) errors.push('Node has an empty id.');
  if (node.type !== 'hydraulic') errors.push(`Node "${node.id}" must use type "hydraulic".`);
  if (!node.data || typeof node.data.type !== 'string') {
    errors.push(`Node "${node.id}" is missing data.type.`);
    return;
  }

  if (!getElementDef(node.data.type)) {
    errors.push(`Node "${node.id}" references unknown element type "${node.data.type}".`);
  }

  if (!isFiniteNumber(node.position?.x) || !isFiniteNumber(node.position?.y)) {
    errors.push(`Node "${node.id}" has an invalid position.`);
  }

  if (!isCardinalRotation(node.data.rotation)) {
    errors.push(`Node "${node.id}" has unsupported rotation "${node.data.rotation}".`);
  }

  if (node.data.lineType !== undefined && !isLineTypeId(node.data.lineType)) {
    errors.push(`Node "${node.id}" references unknown line type "${node.data.lineType}".`);
  }
}

function validateEdge(
  edge: Edge<HydraulicEdgeData>,
  nodeById: Map<string, Node<HydraulicNodeData>>,
  errors: string[],
): void {
  const sourceNode = nodeById.get(edge.source);
  const targetNode = nodeById.get(edge.target);
  const lineType = edge.data?.lineType;

  if (!edge.id) errors.push('Edge has an empty id.');
  if (edge.type !== undefined && edge.type !== 'hydraulic') {
    errors.push(`Edge "${edge.id}" must use type "hydraulic".`);
  }

  if (!sourceNode) {
    errors.push(`Edge "${edge.id}" references missing source node "${edge.source}".`);
  }

  if (!targetNode) {
    errors.push(`Edge "${edge.id}" references missing target node "${edge.target}".`);
  }

  if (!edge.sourceHandle) {
    errors.push(`Edge "${edge.id}" is missing sourceHandle.`);
  } else if (sourceNode && !getNodePortIds(sourceNode).has(edge.sourceHandle)) {
    errors.push(`Edge "${edge.id}" references missing source port "${edge.sourceHandle}".`);
  }

  if (!edge.targetHandle) {
    errors.push(`Edge "${edge.id}" is missing targetHandle.`);
  } else if (targetNode && !getNodePortIds(targetNode).has(edge.targetHandle)) {
    errors.push(`Edge "${edge.id}" references missing target port "${edge.targetHandle}".`);
  }

  if (lineType !== undefined && !isLineTypeId(lineType)) {
    errors.push(`Edge "${edge.id}" references unknown line type "${lineType}".`);
  }

  if (lineType && sourceNode && edge.sourceHandle) {
    const sourcePort = getElementDef(sourceNode.data.type)?.ports.find((port) => port.id === edge.sourceHandle);
    if (sourcePort?.allowedLineTypes && !sourcePort.allowedLineTypes.includes(lineType)) {
      errors.push(`Edge "${edge.id}" line type "${lineType}" is not allowed by source port "${edge.sourceHandle}".`);
    }
  }

  if (lineType && targetNode && edge.targetHandle) {
    const targetPort = getElementDef(targetNode.data.type)?.ports.find((port) => port.id === edge.targetHandle);
    if (targetPort?.allowedLineTypes && !targetPort.allowedLineTypes.includes(lineType)) {
      errors.push(`Edge "${edge.id}" line type "${lineType}" is not allowed by target port "${edge.targetHandle}".`);
    }
  }
}

export function validateDiagramDocument(document: DiagramDocument): string[] {
  const errors: string[] = [];
  const nodeIds = new Set<string>();
  const edgeIds = new Set<string>();
  const nodeById = new Map<string, Node<HydraulicNodeData>>();
  const connectionKeys = new Set<string>();

  for (const node of document.nodes) {
    if (nodeIds.has(node.id)) {
      errors.push(`Duplicate node id "${node.id}".`);
    }
    nodeIds.add(node.id);
    nodeById.set(node.id, node);
    validateNode(node, errors);
  }

  for (const edge of document.edges) {
    if (edgeIds.has(edge.id)) {
      errors.push(`Duplicate edge id "${edge.id}".`);
    }
    edgeIds.add(edge.id);

    const connectionKey = [
      edge.source,
      edge.sourceHandle ?? '',
      edge.target,
      edge.targetHandle ?? '',
    ].join('::');
    if (connectionKeys.has(connectionKey)) {
      errors.push(`Duplicate connection in edge "${edge.id}".`);
    }
    connectionKeys.add(connectionKey);

    validateEdge(edge, nodeById, errors);
  }

  return errors;
}

export function assertValidDiagramDocument(document: DiagramDocument): void {
  const errors = validateDiagramDocument(document);
  if (errors.length > 0) {
    throw new Error(`Файл схемы содержит ошибки:\n${errors.join('\n')}`);
  }
}
