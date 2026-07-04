import { mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { beforeEach, describe, expect, it } from 'vitest';
import {
  addElementToDiagram,
  connectPortsInDiagram,
  createDiagramFile,
  readDiagramFile,
  validateDiagramFile,
} from '@/mcp/diagramFile';

const tmpDir = path.join(process.cwd(), 'tmp', 'mcp-tests');
const diagramPath = path.join('tmp', 'mcp-tests', 'diagram.json');

describe('mcp diagram file tools', () => {
  beforeEach(async () => {
    await rm(tmpDir, { recursive: true, force: true });
    await mkdir(tmpDir, { recursive: true });
  });

  it('creates and reads an empty diagram file', async () => {
    await createDiagramFile({ diagramPath });

    const result = await readDiagramFile({ diagramPath });

    expect(result.document.nodes).toEqual([]);
    expect(result.document.edges).toEqual([]);
    expect(result.document.settings?.activeLineType).toBe('pipe_cold_water');
  });

  it('adds elements and connects their ports', async () => {
    await createDiagramFile({ diagramPath });
    await addElementToDiagram({
      diagramPath,
      type: 'ball-valve',
      id: 'valve-1',
      x: 0,
      y: 0,
    });
    await addElementToDiagram({
      diagramPath,
      type: 'flange',
      id: 'flange-1',
      x: 120,
      y: 0,
    });

    const result = await connectPortsInDiagram({
      diagramPath,
      id: 'edge-1',
      sourceId: 'valve-1',
      sourcePortId: 'outlet',
      targetId: 'flange-1',
      targetPortId: 'inlet',
      lineType: 'pipe_hot_water',
    });

    expect(result.edge).toMatchObject({
      id: 'edge-1',
      source: 'valve-1',
      sourceHandle: 'outlet',
      target: 'flange-1',
      targetHandle: 'inlet',
      data: { lineType: 'pipe_hot_water' },
    });
    expect((await validateDiagramFile({ diagramPath })).errors).toEqual([]);
  });
});
