import { useCallback, type DragEvent } from 'react';
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ConnectionMode,
  useReactFlow,
} from 'reactflow';
import { useDiagramStore } from '../store/diagramStore';
import { nodeTypes } from '../nodes/nodeTypes';
import { edgeTypes } from '../edges/edgeTypes';
import { ELEMENT_DND_TYPE } from './Palette';

const GRID_GAP = 16;

/**
 * The drawing surface. Owns the <ReactFlow> instance and wires it to the
 * store: node/edge changes, connecting, drag-drop of new elements from the
 * palette, grid, snapping and Delete-to-remove.
 */
export function DiagramCanvas() {
  const { screenToFlowPosition } = useReactFlow();

  const nodes = useDiagramStore((s) => s.nodes);
  const edges = useDiagramStore((s) => s.edges);
  const onNodesChange = useDiagramStore((s) => s.onNodesChange);
  const onEdgesChange = useDiagramStore((s) => s.onEdgesChange);
  const onConnect = useDiagramStore((s) => s.onConnect);
  const commitHistoryCheckpoint = useDiagramStore((s) => s.commitHistoryCheckpoint);
  const addElement = useDiagramStore((s) => s.addElement);
  const showGrid = useDiagramStore((s) => s.showGrid);
  const snapToGrid = useDiagramStore((s) => s.snapToGrid);

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData(ELEMENT_DND_TYPE);
      if (!type) return;
      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      addElement(type, position);
    },
    [screenToFlowPosition, addElement],
  );

  return (
    <div className="diagram-canvas" onDrop={onDrop} onDragOver={onDragOver}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStart={commitHistoryCheckpoint}
        onSelectionDragStart={commitHistoryCheckpoint}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        connectionMode={ConnectionMode.Loose}
        deleteKeyCode={['Delete', 'Backspace']}
        snapToGrid={snapToGrid}
        snapGrid={[GRID_GAP, GRID_GAP]}
        defaultEdgeOptions={{ type: 'hydraulic' }}
        minZoom={0.2}
        maxZoom={2.5}
        fitView
      >
        {showGrid && (
          <Background variant={BackgroundVariant.Lines} gap={GRID_GAP} size={1} color="#e2e8f0" />
        )}
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable nodeColor="#94a3b8" maskColor="rgba(148,163,184,0.12)" />
      </ReactFlow>
    </div>
  );
}
