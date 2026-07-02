import type { MouseEvent } from 'react';
import { BaseEdge, EdgeLabelRenderer, Position, type EdgeProps } from 'reactflow';
import type { HydraulicEdgeData, PortDirection } from '../model/types';
import { getElementDef } from '../model/elementCatalog';
import { getLineTypeDef } from '../model/lineTypes';
import { useDiagramStore } from '../store/diagramStore';
import { buildOrthogonalPath } from '../utils/edgeRouting';
import { getRotatedPortDirection } from '../utils/portGeometry';

const POSITION_DIRECTION: Record<Position, PortDirection> = {
  [Position.Left]: 'left',
  [Position.Right]: 'right',
  [Position.Top]: 'top',
  [Position.Bottom]: 'bottom',
};

function getPortDirection(
  nodeType: string | undefined,
  handleId: string | null | undefined,
  rotation: number | undefined,
  fallbackPosition: Position,
): PortDirection {
  const port = nodeType && handleId
    ? getElementDef(nodeType)?.ports.find((candidate) => candidate.id === handleId)
    : undefined;

  if (!port) return POSITION_DIRECTION[fallbackPosition];
  return getRotatedPortDirection(port.direction, rotation);
}

/**
 * Hydraulic pipe edge. The path is built as a pipe route:
 * source port -> source stub -> orthogonal route -> target stub -> target port.
 */
export function HydraulicEdge({
  id,
  source,
  target,
  sourceHandleId,
  targetHandleId,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: EdgeProps<HydraulicEdgeData>) {
  const sourceNode = useDiagramStore((state) => state.nodes.find((node) => node.id === source));
  const targetNode = useDiagramStore((state) => state.nodes.find((node) => node.id === target));
  const deleteEdge = useDiagramStore((state) => state.deleteEdge);
  const sourceDirection = getPortDirection(
    sourceNode?.data.type,
    sourceHandleId,
    sourceNode?.data.rotation,
    sourcePosition,
  );
  const targetDirection = getPortDirection(
    targetNode?.data.type,
    targetHandleId,
    targetNode?.data.rotation,
    targetPosition,
  );
  const path = buildOrthogonalPath(
    { x: sourceX, y: sourceY },
    sourceDirection,
    { x: targetX, y: targetY },
    targetDirection,
    { stubLength: 16 },
  );
  const line = getLineTypeDef(data?.lineType);
  const labelX = (sourceX + targetX) / 2;
  const labelY = (sourceY + targetY) / 2;

  const handleDelete = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    deleteEdge(id);
  };

  return (
    <>
      <BaseEdge
        path={path}
        style={{
          stroke: line.color,
          strokeWidth: selected ? line.strokeWidth + 1.5 : line.strokeWidth,
          strokeDasharray: line.dasharray,
          strokeLinecap: 'butt',
          strokeLinejoin: 'miter',
        }}
      />
      {selected && (
        <EdgeLabelRenderer>
          <button
            type="button"
            className="edge-action edge-action--danger nodrag nopan"
            title="Удалить линию"
            aria-label="Удалить линию"
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            }}
            onMouseDown={(event) => event.stopPropagation()}
            onClick={handleDelete}
          >
            ×
          </button>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
