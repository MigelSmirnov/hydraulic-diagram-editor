import { toPng } from 'html-to-image';

const DEFAULT_EXPORT_FILENAME = 'hydraulic-diagram.png';
const EXPORT_BACKGROUND = '#f1f5f9';

function downloadDataUrl(dataUrl: string, filename: string): void {
  const link = window.document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  link.click();
}

export function getReactFlowViewportElement(): HTMLElement {
  const element = window.document.querySelector<HTMLElement>('.diagram-canvas .react-flow__viewport');

  if (!element) {
    throw new Error('Не удалось найти область схемы для PNG экспорта.');
  }

  return element;
}

export async function exportDiagramPng(filename = DEFAULT_EXPORT_FILENAME): Promise<void> {
  const viewport = getReactFlowViewportElement();
  const dataUrl = await toPng(viewport, {
    backgroundColor: EXPORT_BACKGROUND,
    cacheBust: true,
  });

  downloadDataUrl(dataUrl, filename);
}
