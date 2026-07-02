import type { EdgeTypes } from 'reactflow';
import { HydraulicEdge } from './HydraulicEdge';

/** React Flow edge-type registry. All hydraulic lines share one edge
 *  component that styles itself from its line type. */
export const edgeTypes: EdgeTypes = {
  hydraulic: HydraulicEdge,
};
