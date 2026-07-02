import type { NodeTypes } from 'reactflow';
import { HydraulicNode } from './HydraulicNode';

/** React Flow node-type registry. Add new node kinds here (rarely needed —
 *  most elements share the generic 'hydraulic' node). */
export const nodeTypes: NodeTypes = {
  hydraulic: HydraulicNode,
};
