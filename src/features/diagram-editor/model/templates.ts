import type { DiagramTemplate } from './types';

/**
 * TEMPLATES — predefined starter diagrams.
 * To add a new template: append a DiagramTemplate to `templates`.
 * Node `type` values must exist in elementCatalog.ts and handle ids on edges
 * must be one of: top | right | bottom | left.
 */

export const STARTER_TEMPLATE_ID = 'starter';

export const templates: DiagramTemplate[] = [
  {
    id: STARTER_TEMPLATE_ID,
    name: 'Стартовая схема',
    description:
      'Солнечный коллектор сверху, бойлер справа, насос между ними, расширительный бак рядом, фильтр и кран на вводе воды.',
    nodes: [
      { id: 'solar-1', type: 'solar-collector', position: { x: 320, y: 40 } },
      { id: 'pump-1', type: 'circulation-pump', position: { x: 372, y: 250 } },
      { id: 'tank-1', type: 'expansion-tank', position: { x: 214, y: 238 } },
      { id: 'boiler-1', type: 'indirect-boiler', position: { x: 560, y: 210 } },
      { id: 'water-1', type: 'water-connection', position: { x: 70, y: 470 } },
      { id: 'filter-1', type: 'filter', position: { x: 224, y: 460 } },
      { id: 'valve-1', type: 'ball-valve', position: { x: 370, y: 480 } },
    ],
    edges: [
      { id: 'e-solar-pump', source: 'solar-1', sourceHandle: 'solar_supply', target: 'pump-1', targetHandle: 'inlet', lineType: 'pipe_solar_supply' },
      { id: 'e-pump-boiler', source: 'pump-1', sourceHandle: 'outlet', target: 'boiler-1', targetHandle: 'solar_supply', lineType: 'pipe_solar_supply' },
      { id: 'e-pump-tank', source: 'pump-1', sourceHandle: 'inlet', target: 'tank-1', targetHandle: 'connection', lineType: 'pipe_cold_water' },
      { id: 'e-water-filter', source: 'water-1', sourceHandle: 'outlet', target: 'filter-1', targetHandle: 'inlet', lineType: 'pipe_cold_water' },
      { id: 'e-filter-valve', source: 'filter-1', sourceHandle: 'outlet', target: 'valve-1', targetHandle: 'inlet', lineType: 'pipe_cold_water' },
      { id: 'e-valve-boiler', source: 'valve-1', sourceHandle: 'outlet', target: 'boiler-1', targetHandle: 'cold_in', lineType: 'pipe_cold_water' },
    ],
  },
];

export const templateMap: Record<string, DiagramTemplate> = Object.fromEntries(
  templates.map((t) => [t.id, t]),
);

export function getTemplate(id: string): DiagramTemplate | undefined {
  return templateMap[id];
}
