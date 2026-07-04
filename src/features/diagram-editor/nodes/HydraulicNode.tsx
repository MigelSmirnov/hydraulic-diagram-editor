import { memo, useEffect, useRef, useState, type CSSProperties, type MouseEvent } from 'react';
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
const LONG_RIGHT_CLICK_MS = 250;

interface NodeContextMenuState {
  x: number;
  y: number;
}

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
  const [contextMenu, setContextMenu] = useState<NodeContextMenuState | null>(null);
  const contextTimerRef = useRef<number | null>(null);
  const def = getElementDef(data.type);
  const rotation = normalizeRotation(data.rotation);

  useEffect(() => {
    updateNodeInternals(id);
  }, [id, rotation, updateNodeInternals]);

  useEffect(() => {
    if (!contextMenu) return undefined;

    const closeMenu = () => setContextMenu(null);
    window.addEventListener('click', closeMenu);
    window.addEventListener('keydown', closeMenu);
    return () => {
      window.removeEventListener('click', closeMenu);
      window.removeEventListener('keydown', closeMenu);
    };
  }, [contextMenu]);

  useEffect(() => () => {
    if (contextTimerRef.current !== null) {
      window.clearTimeout(contextTimerRef.current);
    }
  }, []);

  if (!def) {
    return <div className="hydraulic-node hydraulic-node--missing">?</div>;
  }

  const Icon = iconRegistry[def.icon];
  const rotatedSize = getRotatedSymbolSize(
    def.defaultSize.width,
    def.defaultSize.height,
    rotation,
  );

  const clearContextTimer = () => {
    if (contextTimerRef.current === null) return;
    window.clearTimeout(contextTimerRef.current);
    contextTimerRef.current = null;
  };

  const onNodeMouseDown = (event: MouseEvent<HTMLDivElement>) => {
    if (event.button !== 2) return;
    event.preventDefault();
    event.stopPropagation();
    clearContextTimer();
    const rect = event.currentTarget.getBoundingClientRect();
    const menuPosition = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
    contextTimerRef.current = window.setTimeout(() => {
      setContextMenu(menuPosition);
      contextTimerRef.current = null;
    }, LONG_RIGHT_CLICK_MS);
  };

  const onNodeMouseUp = (event: MouseEvent<HTMLDivElement>) => {
    if (event.button !== 2) return;
    event.preventDefault();
    event.stopPropagation();
    clearContextTimer();
  };

  const contextMenuActions = [
    {
      id: 'rotate',
      label: 'Повернуть',
      onSelect: () => rotateNode(id),
    },
    {
      id: 'delete',
      label: 'Удалить',
      danger: true,
      onSelect: () => deleteNode(id),
    },
  ];

  return (
    <div
      className={`hydraulic-node${selected ? ' is-selected' : ''}`}
      style={{ width: rotatedSize.width, height: rotatedSize.height }}
      onContextMenu={(event) => {
        event.preventDefault();
        event.stopPropagation();
      }}
      onMouseDown={onNodeMouseDown}
      onMouseUp={onNodeMouseUp}
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

      {contextMenu && (
        <div
          className="hydraulic-node__context-menu nodrag nopan"
          style={{ left: contextMenu.x, top: contextMenu.y }}
          onClick={(event) => event.stopPropagation()}
          onMouseDown={(event) => event.stopPropagation()}
        >
          {contextMenuActions.map((action) => (
            <button
              key={action.id}
              type="button"
              className={`context-menu__item${action.danger ? ' context-menu__item--danger' : ''}`}
              onClick={() => {
                setContextMenu(null);
                action.onSelect();
              }}
            >
              {action.label}
            </button>
          ))}
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
