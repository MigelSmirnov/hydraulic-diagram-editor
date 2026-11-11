import type { DragEvent } from 'react';
import { useReactFlow } from 'reactflow';
import { categories, elementCatalog } from '../model/elementCatalog';
import { useDiagramStore } from '../store/diagramStore';
import { iconRegistry } from '@/shared/icons';

/** MIME-ish key used to pass the element type through a drag operation. */
export const ELEMENT_DND_TYPE = 'application/hydraulic-element';

/**
 * Catalog-driven palette. Desktop keeps drag-and-drop; tapping an item adds it
 * at the centre of the visible canvas, which makes the same palette usable on
 * touch devices.
 */
export function Palette() {
  const { screenToFlowPosition } = useReactFlow();
  const addElement = useDiagramStore((s) => s.addElement);
  const showPalette = useDiagramStore((s) => s.showPalette);
  const togglePalette = useDiagramStore((s) => s.togglePalette);

  const onDragStart = (event: DragEvent, type: string) => {
    event.dataTransfer.setData(ELEMENT_DND_TYPE, type);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onAddAtViewportCentre = (type: string) => {
    const position = screenToFlowPosition({
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
    });
    addElement(type, position);

    if (showPalette && window.matchMedia('(max-width: 760px)').matches) {
      togglePalette();
    }
  };

  return (
    <aside className="palette">
      <div className="mobile-sheet__handle" aria-hidden />
      <h2 className="panel-title">Элементы</h2>

      <div className="palette__scroll">
        {categories.map((cat) => {
          const items = elementCatalog.filter((e) => e.category === cat.id);
          if (items.length === 0) return null;

          return (
            <section key={cat.id} className="palette__group">
              <div className="palette__group-title">{cat.label}</div>
              {items.map((el) => {
                const Icon = iconRegistry[el.icon];
                return (
                  <button
                    key={el.type}
                    className="palette__item"
                    type="button"
                    draggable
                    onDragStart={(e) => onDragStart(e, el.type)}
                    onClick={() => onAddAtViewportCentre(el.type)}
                    title={el.label}
                  >
                    <span className="palette__item-icon">{Icon ? <Icon /> : null}</span>
                    <span className="palette__item-label">{el.label}</span>
                  </button>
                );
              })}
            </section>
          );
        })}
      </div>

      <p className="palette__hint">Перетащите элемент или нажмите, чтобы добавить в центр</p>
    </aside>
  );
}
