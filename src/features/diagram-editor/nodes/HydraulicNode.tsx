import { memo, useEffect, type CSSProperties, type MouseEvent } from 'react';
import { Handle, Position, type NodeProps, useUpdateNodeInternals } from 'reactflow';
import type { ElementPort, HandleId, HydraulicNodeData } from '../model/types';
import { getElementDef } from '../model/elementCatalog';
import { getLineTypeDef } from '../model/lineTypes';
import { useDiagramStore } from '../store/diagramStore';
import {
  getRotatedPortDirection,
  getRotatedPortPosition,
  getRotatedSymbolSize,
  normalizeRotation,
} from '../utils/portGeometry';
import { iconRegistry } from '@/shared/icons';

const HANDLE_POSITION: Record<HandleId, Position> = {
  top: Position.Top,
  right: Position.Right,
  bottom: Position.Bottom,
  left: Position.Left,
};

function getPortStyle(port: ElementPort, width: number, height: number, rotation: number): CSSProperties {
  const point = getRotatedPortPosition(port, width, height, rotation);
  const size = getRotatedSymbolSize(width, height, rotation);
  return {
    left: `${(point.x / size.width) * 100}%`,
    top: `${(point.y / size.height) * 100}%`,
  };
}

function getPortLabelStyle(port: ElementPort, width: number, height: number, rotation: number): CSSProperties {
  const point = getRotatedPortPosition(port, width, height, rotation);
  const size = getRotatedSymbolSize(width, height, rotation);
  const direction = getRotatedPortDirection(port.direction, rotation);
  const base: CSSProperties = {
    left: `${(point.x / size.width) * 100}%`,
    top: `${(point.y / size.height) * 100}%`,
  };

  if (direction === 'left') return { ...base, transform: 'translate(calc(-100% - 8px), -50%)', textAlign: 'right' };
  if (direction === 'right') return { ...base, transform: 'translate(8px, -50%)', textAlign: 'left' };
  if (direction === 'top') return { ...base, transform: 'translate(-50%, calc(-100% - 6px))', textAlign: 'center' };
  return { ...base, transform: 'translate(-50%, 8px)', textAlign: 'center' };
}

/**
 * The single generic node. Every hydraulic element renders through this
 * component; its appearance and ports come entirely from the catalog
 * definition, so adding an element never means writing a new node component.
 *
 * All ports are rendered as `source` handles; the canvas runs in ConnectionMode.Loose
 * so any handle can connect to any other regardless of direction.
 */
function HydraulicNodeComponent({ id, data, selected }: NodeProps<HydraulicNodeData>) {
  const updateNodeInternals = useUpdateNodeInternals();
  const rotateNode = useDiagramStore((s) => s.rotateNode);
  const deleteNode = useDiagramStore((s) => s.deleteNode);
  const def = getElementDef(data.type);
  const rotation = normalizeRotation(data.rotation);

  useEffect(() => {
    updateNodeInternals(id);
  }, [id, rotation, updateNodeInternals]);

  if (!def) {
    return <div className="hydraulic-node hydraulic-node--missing">?</div>;
  }

  const Icon = iconRegistry[def.icon];
  const rotatedSize = getRotatedSymbolSize(
    def.defaultSize.width,
    def.defaultSize.height,
    rotation,
  );

  const stopActionPropagation = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
  };

  return (
    <div
      className={`hydraulic-node${selected ? ' is-selected' : ''}`}
      style={{ width: rotatedSize.width, height: rotatedSize.height }}
    >
      <div
        className="hydraulic-node__symbol"
        style={{
          width: def.defaultSize.width,
          height: def.defaultSize.height,
          transform: `translate(-50%, -50%) rotate(${rotation}deg)`,
          color: def.tintFromLineType ? getLineTypeDef(data.lineType).color : undefined,
        }}
      >
        {Icon ? <Icon /> : null}
      </div>

      {selected && (
        <div className="hydraulic-node__actions nodrag nopan">
          <button
            type="button"
            className="node-action"
            title="Повернуть"
            aria-label="Повернуть элемент"
            onMouseDown={stopActionPropagation}
            onClick={(event) => {
              event.stopPropagation();
              rotateNode(id);
            }}
          >
            ↻
          </button>
          <button
            type="button"
            className="node-action node-action--danger"
            title="Удалить"
            aria-label="Удалить элемент"
            onMouseDown={stopActionPropagation}
            onClick={(event) => {
              event.stopPropagation();
              deleteNode(id);
            }}
          >
            ×
          </button>
        </div>
      )}

      {def.ports
        .filter((port) => port.showLabel)
        .map((port) => (
          <div
            key={`${port.id}-label`}
            className="hydraulic-node__port-label"
            style={getPortLabelStyle(port, def.defaultSize.width, def.defaultSize.height, rotation)}
          >
            {port.label}
          </div>
        ))}

      {def.ports.map((port) => (
        <Handle
          key={port.id}
          id={port.id}
          type="source"
          position={HANDLE_POSITION[getRotatedPortDirection(port.direction, rotation)]}
          className="hydraulic-handle"
          title={port.label}
          style={getPortStyle(port, def.defaultSize.width, def.defaultSize.height, rotation)}
        />
      ))}
    </div>
  );
}

export const HydraulicNode = memo(HydraulicNodeComponent);
