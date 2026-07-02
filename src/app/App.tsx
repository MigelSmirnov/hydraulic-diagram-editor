import { AppProviders } from './providers/AppProviders';
import { Toolbar } from '@/features/diagram-editor/components/Toolbar';
import { Palette } from '@/features/diagram-editor/components/Palette';
import { DiagramCanvas } from '@/features/diagram-editor/components/DiagramCanvas';
import { PropertiesPanel } from '@/features/diagram-editor/components/PropertiesPanel';
import { useDiagramStore } from '@/features/diagram-editor/store/diagramStore';

/**
 * Application shell. Pure layout composition — NO business logic lives here.
 * Everything meaningful happens inside features/diagram-editor.
 *
 * Side panels are collapsible; the grid columns follow whichever are shown so
 * the canvas reclaims the freed space and nothing is pushed off-screen.
 */
export default function App() {
  const showPalette = useDiagramStore((s) => s.showPalette);
  const showProperties = useDiagramStore((s) => s.showProperties);

  const gridTemplateColumns = [
    showPalette ? '248px' : null,
    'minmax(0, 1fr)',
    showProperties ? '280px' : null,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <AppProviders>
      <div className="app-shell">
        <Toolbar />
        <div className="app-body" style={{ gridTemplateColumns }}>
          {showPalette && <Palette />}
          <DiagramCanvas />
          {showProperties && <PropertiesPanel />}
        </div>
      </div>
    </AppProviders>
  );
}
