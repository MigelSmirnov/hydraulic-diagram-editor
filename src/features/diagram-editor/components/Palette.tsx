import type { DragEvent } from 'react';
import { categories, elementCatalog } from '../model/elementCatalog';
import { iconRegistry } from '@/shared/icons';

/** MIME-ish key used to pass the element type through a drag operation. */
export const ELEMENT_DND_TYPE = 'application/hydraulic-element';

/**
 * Left palette. Lists catalog elements grouped by category. Each item is
 * draggable; DiagramCanvas reads the element type from the drag payload and
 * creates a node at the drop position. Purely driven by elementCatalog.ts.
 */
export function Palette() {
  const onDragStart = (event: DragEvent, type: string) => {
    event.dataTransfer.setData(ELEMENT_DND_TYPE, type);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="palette">
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
                  <div
                    key={el.type}
                    className="palette__item"
                    draggable
                    onDragStart={(e) => onDragStart(e, el.type)}
                    title={el.label}
                  >
                    <span className="palette__item-icon">{Icon ? <Icon /> : null}</span>
                    <span className="palette__item-label">{el.label}</span>
                  </div>
                );
              })}
            </section>
          );
        })}
      </div>

      <p className="palette__hint">Перетащите элемент на полотно</p>
    </aside>
  );
}
