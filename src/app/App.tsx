import { AppProviders } from './providers/AppProviders';
import { Toolbar } from '@/features/diagram-editor/components/Toolbar';
import { Palette } from '@/features/diagram-editor/components/Palette';
import { DiagramCanvas } from '@/features/diagram-editor/components/DiagramCanvas';
import { PropertiesPanel } from '@/features/diagram-editor/components/PropertiesPanel';

/**
 * Application shell. Pure layout composition — NO business logic lives here.
 * Everything meaningful happens inside features/diagram-editor.
 */
export default function App() {
  return (
    <AppProviders>
      <div className="app-shell">
        <Toolbar />
        <div className="app-body">
          <Palette />
          <DiagramCanvas />
          <PropertiesPanel />
        </div>
      </div>
    </AppProviders>
  );
}
