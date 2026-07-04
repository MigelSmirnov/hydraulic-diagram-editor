import { useRef, type ChangeEvent } from 'react';
import { useReactFlow } from 'reactflow';
import { useDiagramStore } from '../store/diagramStore';
import { lineTypes } from '../model/lineTypes';
import { STARTER_TEMPLATE_ID } from '../model/templates';
import {
  deserializeDiagram,
  downloadDiagramJson,
  readDiagramJsonFile,
  serializeDiagram,
} from '../persistence';

/**
 * Top toolbar. Editor-wide controls only — no diagram logic beyond calling
 * store actions: grid toggle, snap toggle, line-type selector, clear, demo.
 */
export function Toolbar() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { getViewport, setViewport } = useReactFlow();

  const nodes = useDiagramStore((s) => s.nodes);
  const edges = useDiagramStore((s) => s.edges);
  const showGrid = useDiagramStore((s) => s.showGrid);
  const snapToGrid = useDiagramStore((s) => s.snapToGrid);
  const showPalette = useDiagramStore((s) => s.showPalette);
  const showProperties = useDiagramStore((s) => s.showProperties);
  const selectedLineType = useDiagramStore((s) => s.selectedLineType);
  const canUndo = useDiagramStore((s) => s.past.length > 0);
  const canRedo = useDiagramStore((s) => s.future.length > 0);
  const toggleGrid = useDiagramStore((s) => s.toggleGrid);
  const toggleSnap = useDiagramStore((s) => s.toggleSnap);
  const togglePalette = useDiagramStore((s) => s.togglePalette);
  const toggleProperties = useDiagramStore((s) => s.toggleProperties);
  const undo = useDiagramStore((s) => s.undo);
  const redo = useDiagramStore((s) => s.redo);
  const clear = useDiagramStore((s) => s.clear);
  const loadTemplate = useDiagramStore((s) => s.loadTemplate);
  const replaceDiagram = useDiagramStore((s) => s.replaceDiagram);
  const setLineType = useDiagramStore((s) => s.setLineType);

  const handleClear = () => {
    if (confirm('Очистить полотно? Все элементы и линии будут удалены.')) clear();
  };

  const handleSaveJson = () => {
    const document = serializeDiagram({
      nodes,
      edges,
      viewport: getViewport(),
      settings: {
        showGrid,
        snapToGrid,
        activeLineType: selectedLineType,
      },
    });

    downloadDiagramJson(document);
  };

  const handleLoadJson = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    try {
      const rawDocument = await readDiagramJsonFile(file);
      const document = deserializeDiagram(rawDocument);
      replaceDiagram({
        nodes: document.nodes,
        edges: document.edges,
        settings: document.settings,
      });
      if (document.viewport) setViewport(document.viewport);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Не удалось загрузить JSON файл схемы.');
    }
  };

  return (
    <header className="toolbar">
      <div className="toolbar__brand">
        <span className="toolbar__logo" aria-hidden>≋</span>
        <span>Редактор гидравлических схем</span>
      </div>

      <div className="toolbar__group">
        <button
          className={`btn${showPalette ? ' btn--active' : ''}`}
          onClick={togglePalette}
          aria-pressed={showPalette}
          title="Показать/скрыть панель элементов"
        >
          Элементы
        </button>
        <button
          className={`btn${showProperties ? ' btn--active' : ''}`}
          onClick={toggleProperties}
          aria-pressed={showProperties}
          title="Показать/скрыть панель свойств"
        >
          Свойства
        </button>
      </div>

      <div className="toolbar__group">
        <button className="btn" onClick={toggleGrid}>
          {showGrid ? 'Скрыть сетку' : 'Показать сетку'}
        </button>
        <button
          className={`btn${snapToGrid ? ' btn--active' : ''}`}
          onClick={toggleSnap}
          aria-pressed={snapToGrid}
        >
          Привязка: {snapToGrid ? 'вкл' : 'выкл'}
        </button>
      </div>

      <label className="toolbar__field">
        <span>Тип линии</span>
        <select
          value={selectedLineType}
          onChange={(e) => setLineType(e.target.value)}
        >
          {lineTypes.map((lt) => (
            <option key={lt.id} value={lt.id}>
              {lt.label}
            </option>
          ))}
        </select>
      </label>

      <div className="line-legend" aria-label="Легенда типов линий">
        {lineTypes.map((lineType) => (
          <div key={lineType.id} className="line-legend__item" title={lineType.description}>
            <svg className="line-legend__sample" viewBox="0 0 40 8" aria-hidden>
              <line
                x1="2"
                y1="4"
                x2="38"
                y2="4"
                stroke={lineType.color}
                strokeWidth={lineType.strokeWidth}
                strokeDasharray={lineType.dasharray}
                strokeLinecap="round"
              />
            </svg>
            <span className="line-legend__label">{lineType.label}</span>
          </div>
        ))}
      </div>

      <div className="toolbar__group toolbar__group--end">
        <button className="btn" onClick={undo} disabled={!canUndo} title="Отменить действие">
          Undo
        </button>
        <button className="btn" onClick={redo} disabled={!canRedo} title="Повторить действие">
          Redo
        </button>
        <button className="btn" onClick={handleSaveJson}>
          Save JSON
        </button>
        <button className="btn" onClick={() => fileInputRef.current?.click()}>
          Load JSON
        </button>
        <input
          ref={fileInputRef}
          className="visually-hidden"
          type="file"
          accept="application/json,.json"
          onChange={handleLoadJson}
        />
        <button className="btn" onClick={() => loadTemplate(STARTER_TEMPLATE_ID)}>
          Загрузить демо
        </button>
        <button className="btn btn--danger" onClick={handleClear}>
          Очистить
        </button>
      </div>
    </header>
  );
}
