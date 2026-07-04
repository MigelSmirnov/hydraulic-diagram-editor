#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { elementCatalog } from '../features/diagram-editor/model/elementCatalog';
import { lineTypes } from '../features/diagram-editor/model/lineTypes';
import {
  addElementToDiagram,
  connectPortsInDiagram,
  createDiagramFile,
  readDiagramFile,
  updateElementInDiagram,
  validateDiagramFile,
} from './diagramFile';
import { renderDiagramPng } from './renderPng';

function textJson(value: unknown) {
  return {
    content: [
      {
        type: 'text' as const,
        text: JSON.stringify(value, null, 2),
      },
    ],
  };
}

const diagramPathSchema = {
  diagramPath: z.string().optional().describe('Path inside the project root. Defaults to HYDRAULIC_DIAGRAM_FILE or hydraulic-diagram.agent.json.'),
};

const rotationSchema = z.union([z.literal(0), z.literal(90), z.literal(180), z.literal(270)]);

const server = new McpServer({
  name: 'hydraulic-diagram-editor',
  version: '0.1.0',
});

server.registerTool(
  'hydraulic_list_catalog',
  {
    title: 'List hydraulic catalog',
    description: 'List available hydraulic element types, ports, and line types.',
  },
  async () => textJson({ elements: elementCatalog, lineTypes }),
);

server.registerTool(
  'hydraulic_create_diagram',
  {
    title: 'Create hydraulic diagram',
    description: 'Create an empty hydraulic diagram JSON file.',
    inputSchema: {
      ...diagramPathSchema,
      overwrite: z.boolean().optional().describe('Overwrite the file if it already exists. Defaults to false.'),
    },
  },
  async (input) => textJson(await createDiagramFile(input)),
);

server.registerTool(
  'hydraulic_read_diagram',
  {
    title: 'Read hydraulic diagram',
    description: 'Read and validate a hydraulic diagram JSON file.',
    inputSchema: diagramPathSchema,
  },
  async (input) => textJson(await readDiagramFile(input)),
);

server.registerTool(
  'hydraulic_add_element',
  {
    title: 'Add hydraulic element',
    description: 'Add an element from the catalog to a diagram file. Creates the diagram file if it does not exist.',
    inputSchema: {
      ...diagramPathSchema,
      type: z.string().describe('Element type from hydraulic_list_catalog.'),
      x: z.number().describe('Node x position on the canvas.'),
      y: z.number().describe('Node y position on the canvas.'),
      id: z.string().optional().describe('Optional explicit node id.'),
      label: z.string().optional().describe('Optional label override.'),
      rotation: rotationSchema.optional(),
      lineType: z.string().optional().describe('Optional line type used to tint elements that support line tinting.'),
    },
  },
  async (input) => textJson(await addElementToDiagram(input)),
);

server.registerTool(
  'hydraulic_update_element',
  {
    title: 'Update hydraulic element',
    description: 'Update an existing diagram element position, label, rotation or line tint.',
    inputSchema: {
      ...diagramPathSchema,
      nodeId: z.string().describe('Existing node id to update.'),
      x: z.number().optional().describe('New node x position. Omit to keep the current x.'),
      y: z.number().optional().describe('New node y position. Omit to keep the current y.'),
      label: z.string().optional().describe('New label. Omit to keep the current label.'),
      rotation: rotationSchema.optional().describe('New rotation in degrees. Omit to keep the current rotation.'),
      lineType: z.string().optional().describe('New line type used to tint elements that support line tinting. Omit to keep the current tint.'),
    },
  },
  async (input) => textJson(await updateElementInDiagram(input)),
);

server.registerTool(
  'hydraulic_connect_ports',
  {
    title: 'Connect hydraulic ports',
    description: 'Connect two element ports in a diagram file.',
    inputSchema: {
      ...diagramPathSchema,
      sourceId: z.string(),
      sourcePortId: z.string(),
      targetId: z.string(),
      targetPortId: z.string(),
      lineType: z.string().optional(),
      id: z.string().optional().describe('Optional explicit edge id.'),
    },
  },
  async (input) => textJson(await connectPortsInDiagram(input)),
);

server.registerTool(
  'hydraulic_validate_diagram',
  {
    title: 'Validate hydraulic diagram',
    description: 'Validate a hydraulic diagram JSON file and return validation errors.',
    inputSchema: diagramPathSchema,
  },
  async (input) => textJson(await validateDiagramFile(input)),
);

server.registerTool(
  'hydraulic_render_png',
  {
    title: 'Render hydraulic diagram PNG',
    description: 'Render a diagram JSON file through the real React editor UI and save a canvas PNG screenshot.',
    inputSchema: {
      ...diagramPathSchema,
      outputPath: z.string().optional().describe('PNG path inside the project root. Defaults to exports/agent-preview.png.'),
      width: z.number().int().min(320).optional().describe('Browser viewport width. Defaults to 1280.'),
      height: z.number().int().min(240).optional().describe('Browser viewport height. Defaults to 900.'),
      timeoutMs: z.number().int().min(1000).optional().describe('Render timeout in milliseconds. Defaults to 30000.'),
    },
  },
  async (input) => textJson(await renderDiagramPng(input)),
);

const transport = new StdioServerTransport();
await server.connect(transport);
