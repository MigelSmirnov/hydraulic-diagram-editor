import type { ReactNode } from 'react';
import { ReactFlowProvider } from 'reactflow';

/**
 * Global providers. Kept separate from App so the shell stays declarative and
 * new providers (theme, i18n, undo/redo) can be added in one place.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return <ReactFlowProvider>{children}</ReactFlowProvider>;
}
