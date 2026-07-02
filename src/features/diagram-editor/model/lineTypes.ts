import type { LineTypeDef, LineTypeId } from './types';

/**
 * LINE TYPES — single source of truth for pipe / cable line kinds.
 *
 * To add a new line type: append an entry here. UI components and edges must
 * consume this catalog instead of hardcoding ids, labels or visual styles.
 */
export const lineTypes: LineTypeDef[] = [
  {
    id: 'pipe_cold_water',
    label: 'ХВС',
    category: 'water',
    visualStyle: 'solid',
    color: '#2563eb',
    strokeWidth: 2,
    description: 'Трубопровод холодного водоснабжения.',
  },
  {
    id: 'pipe_hot_water',
    label: 'ГВС',
    category: 'water',
    visualStyle: 'solid',
    color: '#dc2626',
    strokeWidth: 2,
    description: 'Трубопровод горячего водоснабжения.',
  },
  {
    id: 'pipe_dhw_recirculation',
    label: 'Рециркуляция ГВС',
    category: 'water',
    visualStyle: 'dashed',
    color: '#f97316',
    strokeWidth: 2,
    dasharray: '7 4',
    description: 'Линия рециркуляции горячего водоснабжения.',
  },
  {
    id: 'pipe_solar_supply',
    label: 'Солнечный контур подача',
    category: 'solar',
    visualStyle: 'solid',
    color: '#e11d48',
    strokeWidth: 2.5,
    description: 'Подающая линия солнечного контура.',
  },
  {
    id: 'pipe_solar_return',
    label: 'Солнечный контур обратка',
    category: 'solar',
    visualStyle: 'dashed',
    color: '#0ea5e9',
    strokeWidth: 2.5,
    dasharray: '10 4',
    description: 'Обратная линия солнечного контура.',
  },
  {
    id: 'pipe_drain',
    label: 'Дренаж / сброс',
    category: 'drain',
    visualStyle: 'dashed',
    color: '#65a30d',
    strokeWidth: 2,
    dasharray: '4 4',
    description: 'Дренажная или сбросная линия.',
  },
  {
    id: 'control_cable',
    label: 'Управляющий кабель / датчик',
    category: 'control',
    visualStyle: 'dotted',
    color: '#7c3aed',
    strokeWidth: 1.5,
    dasharray: '2 4',
    description: 'Сигнальная или управляющая связь датчика.',
  },
];

export const DEFAULT_LINE_TYPE: LineTypeId = 'pipe_cold_water';

const lineTypeMap = Object.fromEntries(
  lineTypes.map((lineType) => [lineType.id, lineType]),
) as Record<string, LineTypeDef>;

export function getLineTypeDef(id?: string): LineTypeDef {
  return lineTypeMap[id as LineTypeId] ?? lineTypeMap[DEFAULT_LINE_TYPE] ?? lineTypes[0];
}

export function isLineTypeId(id: string): boolean {
  return lineTypes.some((lineType) => lineType.id === id);
}
