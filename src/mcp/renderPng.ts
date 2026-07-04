import { mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { chromium, type Browser } from 'playwright';
import { createServer, type ViteDevServer } from 'vite';
import { DIAGRAM_AUTOSAVE_KEY } from '../features/diagram-editor/persistence/diagramAutosave';
import { readDiagramFile, resolveDiagramPath, type DiagramPathInput } from './diagramFile';

const DEFAULT_OUTPUT_FILE = 'exports/agent-preview.png';
const DEFAULT_VIEWPORT = { width: 1280, height: 900 };
const DEFAULT_TIMEOUT_MS = 30_000;

export interface RenderPngInput extends DiagramPathInput {
  outputPath?: string;
  width?: number;
  height?: number;
  timeoutMs?: number;
}

export interface RenderPngResult {
  diagramPath: string;
  outputPath: string;
  byteSize: number;
  width: number;
  height: number;
  nodeCount: number;
  edgeCount: number;
}

function resolveProjectPath(inputPath: string): string {
  const resolvedPath = path.resolve(process.cwd(), inputPath);
  const projectRoot = `${process.cwd()}${path.sep}`;

  if (resolvedPath !== process.cwd() && !resolvedPath.startsWith(projectRoot)) {
    throw new Error(`Path must stay inside project root: ${inputPath}`);
  }

  return resolvedPath;
}

async function startViteServer(): Promise<{ server: ViteDevServer; url: string }> {
  const server = await createServer({
    configFile: path.resolve(process.cwd(), 'vite.config.ts'),
    logLevel: 'error',
    server: {
      host: '127.0.0.1',
      port: 0,
    },
  });

  await server.listen();
  const url = server.resolvedUrls?.local[0];
  if (!url) {
    await server.close();
    throw new Error('Vite did not expose a local URL for screenshot rendering.');
  }

  return { server, url };
}

export async function renderDiagramPng(input: RenderPngInput = {}): Promise<RenderPngResult> {
  const { document } = await readDiagramFile(input);
  const outputPath = resolveProjectPath(input.outputPath ?? DEFAULT_OUTPUT_FILE);
  const width = input.width ?? DEFAULT_VIEWPORT.width;
  const height = input.height ?? DEFAULT_VIEWPORT.height;
  const timeoutMs = input.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  let viteServer: ViteDevServer | undefined;
  let browser: Browser | undefined;

  if (width < 320 || height < 240) {
    throw new Error('PNG viewport must be at least 320x240.');
  }

  try {
    const vite = await startViteServer();
    viteServer = vite.server;
    browser = await chromium.launch({ headless: true });

    const context = await browser.newContext({
      viewport: { width, height },
      deviceScaleFactor: 1,
    });
    await context.addInitScript(
      ({ key, serializedDocument }) => {
        window.localStorage.setItem(key, serializedDocument);
      },
      {
        key: DIAGRAM_AUTOSAVE_KEY,
        serializedDocument: JSON.stringify(document),
      },
    );

    const page = await context.newPage();
    await page.goto(vite.url, { waitUntil: 'networkidle', timeout: timeoutMs });
    await page.waitForSelector('.diagram-canvas .react-flow', { timeout: timeoutMs });

    if (document.nodes.length > 0) {
      await page.waitForFunction(
        (nodeCount) => window.document.querySelectorAll('.react-flow__node').length >= nodeCount,
        document.nodes.length,
        { timeout: timeoutMs },
      );
    }

    const fitViewButton = page.locator('.react-flow__controls-fitview');
    if ((await fitViewButton.count()) > 0) {
      await fitViewButton.first().click();
      await page.waitForTimeout(250);
    }

    await mkdir(path.dirname(outputPath), { recursive: true });
    await page.locator('.diagram-canvas').screenshot({
      path: outputPath,
      animations: 'disabled',
    });

    const fileStat = await stat(outputPath);
    return {
      diagramPath: resolveDiagramPath(input.diagramPath),
      outputPath,
      byteSize: fileStat.size,
      width,
      height,
      nodeCount: document.nodes.length,
      edgeCount: document.edges.length,
    };
  } finally {
    await browser?.close();
    await viteServer?.close();
  }
}
