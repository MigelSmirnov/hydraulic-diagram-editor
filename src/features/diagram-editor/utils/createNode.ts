import type { Node } from 'reactflow';
import { getElementDef } from '@/features/diagram-editor/model/elementCatalog';
import type { HydraulicNodeData } from '@/features/diagram-editor/model/types';
import { createId } from '@/lib/id';

/**
 * Builds a React Flow node from a catalog element type.
 * This is the only place that knows how to translate a domain element into a
 * React Flow node structure.
 */
export function createNode(
  type: string,
  position: { x: number; y: number },
  id?: string,
  labelOverride?: string,
): Node<HydraulicNodeData> {
  const def = getElementDef(type);
  if (!def) {
    throw new Error(`createNode: unknown element type "${type}"`);
  }

  return {
    id: id ?? createId(type),
    type: 'hydraulic', // all elements render through the generic HydraulicNode
    position,
    data: {
      type: def.type,
      label: labelOverride ?? def.label,
      rotation: 0,
    },
  };
}
