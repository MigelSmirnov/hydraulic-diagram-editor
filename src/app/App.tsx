import { AppProviders } from './providers/AppProviders';
import { Toolbar } from '@/features/diagram-editor/components/Toolbar';
import { Palette } from '@/features/diagram-editor/components/Palette';
import { DiagramCanvas } from '@/features/diagram-editor/components/DiagramCanvas';
import { PropertiesPanel } from '@/features/diagram-editor/components/PropertiesPanel';
import { DiagramAutosave } from '@/features/diagram-editor/components/DiagramAutosave';
import { useDiagramStore } from '@/features/diagram-editor/store/diagramStore';

/**
 * Application shell. Desktop uses a three-column grid. Mobile CSS turns the
 * side panels into bottom sheets over a full-screen canvas.
 */
export default function App() {
  const showPalette = useDiagramStore((s) => s.showPalette);
  const showProperties = useDiagramStore((s) => s.showProperties);
  const togglePalette = useDiagramStore((s) => s.togglePalette);
  const toggleProperties = useDiagramStore((s) => s.toggleProperties);

  const gridTemplateColumns = [
    showPalette ? '248px' : null,
    'minmax(0, 1fr)',
    showProperties ? '280px' : null,
  ]
    .filter(Boolean)
    .join(' ');

  const closePanels = () => {
    if (showPalette) togglePalette();
    if (showProperties) toggleProperties();
  };

  return (
    <AppProviders>
      <DiagramAutosave />
      <div className="app-shell">
        <Toolbar />
        <div className="app-body" style={{ gridTemplateColumns }}>
          {(showPalette || showProperties) && (
            <button
              className="mobile-sheet-backdrop"
              type="button"
              aria-label="Закрыть панель"
              onClick={closePanels}
            />
          )}

          {showPalette && (
            <div className="mobile-sheet mobile-sheet--palette">
              <Palette />
            </div>
          )}

          <DiagramCanvas />

          {showProperties && (
            <div className="mobile-sheet mobile-sheet--properties">
              <PropertiesPanel />
            </div>
          )}
        </div>
      </div>
    </AppProviders>
  );
}
