import { useDiagramStore } from '../store/diagramStore';
import { getElementDef } from '../model/elementCatalog';
import { DEFAULT_LINE_TYPE, getLineTypeDef, lineTypes } from '../model/lineTypes';
import { PropertyRow } from '@/shared/ui/PropertyRow';

/**
 * Right panel. Shows read-only properties of the currently selected node or
 * edge (id / type / label). Editing lands in a later version — see roadmap.
 */
export function PropertiesPanel() {
  const node = useDiagramStore((s) => s.nodes.find((n) => n.selected));
  const edge = useDiagramStore((s) => s.edges.find((e) => e.selected));
  const updateEdgeLineType = useDiagramStore((s) => s.updateEdgeLineType);
  const selectedEdgeLineType = getLineTypeDef(edge?.data?.lineType);

  return (
    <aside className="properties">
      <h2 className="panel-title">Свойства</h2>

      {!node && !edge && (
        <p className="properties__empty">Выберите элемент или линию на полотне</p>
      )}

      {node && (
        <div className="properties__body">
          <div className="properties__kind">Элемент</div>
          <PropertyRow label="ID" value={node.id} mono />
          <PropertyRow label="Тип" value={node.data.type} mono />
          <PropertyRow label="Название" value={node.data.label} />
          <PropertyRow
            label="Категория"
            value={getElementDef(node.data.type)?.category ?? '—'}
          />
        </div>
      )}

      {edge && (
        <div className="properties__body">
          <div className="properties__kind">Линия</div>
          <PropertyRow label="ID" value={edge.id} mono />
          <PropertyRow label="Source" value={edge.source} mono />
          <PropertyRow label="Target" value={edge.target} mono />
          <PropertyRow label="Line type" value={selectedEdgeLineType.id} mono />
          <PropertyRow
            label="Тип линии"
            value={
              <select
                className="property-select"
                value={selectedEdgeLineType.id}
                onChange={(event) =>
                  updateEdgeLineType(edge.id, event.target.value)
                }
              >
                {lineTypes.map((lineType) => (
                  <option key={lineType.id} value={lineType.id}>
                    {lineType.label}
                  </option>
                ))}
              </select>
            }
          />
          <PropertyRow label="Label" value={selectedEdgeLineType.label} />
          {edge.data?.lineType && edge.data.lineType !== selectedEdgeLineType.id && (
            <PropertyRow label="Fallback" value={DEFAULT_LINE_TYPE} mono />
          )}
        </div>
      )}
    </aside>
  );
}
