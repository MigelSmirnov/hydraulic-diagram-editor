import type { CategoryDef, HydraulicElementDef } from './types';

/**
 * ELEMENT CATALOG — the single source of truth for all hydraulic elements.
 *
 * To add a new element:
 *   1. Add (or reuse) an icon in src/shared/icons and register it in index.ts.
 *   2. Append an entry to `elementCatalog` below.
 * Nothing else needs to change — the palette, canvas node and properties
 * panel all read from here.
 *
 * Full recipe + port-geometry rules: docs/adding-elements.md.
 * Inline flow-through fittings share one pipe axis: height 74, left/right
 * ports at y = 37, so runs stay straight.
 */

export const categories: CategoryDef[] = [
  { id: 'solar', label: 'Солнечный контур' },
  { id: 'storage', label: 'Накопители' },
  { id: 'pumps', label: 'Насосы' },
  { id: 'valves', label: 'Арматура' },
  { id: 'treatment', label: 'Водоподготовка' },
  { id: 'instruments', label: 'КИПиА' },
  { id: 'connections', label: 'Подключения' },
];

export const elementCatalog: HydraulicElementDef[] = [
  {
    type: 'solar-collector',
    label: 'Солнечный коллектор',
    category: 'solar',
    icon: 'solar-collector',
    defaultSize: { width: 140, height: 92 },
    ports: [
      { id: 'solar_supply', label: 'Подача', side: 'bottom', direction: 'bottom', x: 52, y: 92, kind: 'solar_supply', allowedLineTypes: ['pipe_solar_supply'] },
      { id: 'solar_return', label: 'Обратка', side: 'bottom', direction: 'bottom', x: 88, y: 92, kind: 'solar_return', allowedLineTypes: ['pipe_solar_return'] },
    ],
  },
  {
    type: 'indirect-boiler',
    label: 'Бойлер косвенного нагрева',
    category: 'storage',
    icon: 'boiler',
    defaultSize: { width: 96, height: 132 },
    ports: [
      { id: 'cold_in', label: 'ХВС вход', side: 'left', direction: 'left', x: 0, y: 106, kind: 'inlet', allowedLineTypes: ['pipe_cold_water'], showLabel: true },
      { id: 'hot_out', label: 'ГВС выход', side: 'right', direction: 'right', x: 96, y: 24, kind: 'outlet', allowedLineTypes: ['pipe_hot_water'] },
      { id: 'solar_supply', label: 'Змеевик подача', side: 'left', direction: 'left', x: 0, y: 72, kind: 'solar_supply', allowedLineTypes: ['pipe_solar_supply'], showLabel: true },
      { id: 'solar_return', label: 'Змеевик обратка', side: 'left', direction: 'left', x: 0, y: 96, kind: 'solar_return', allowedLineTypes: ['pipe_solar_return'], showLabel: true },
      { id: 'drain', label: 'Дренаж', side: 'bottom', direction: 'bottom', x: 48, y: 132, kind: 'drain', allowedLineTypes: ['pipe_drain'] },
    ],
  },
  {
    type: 'expansion-tank',
    label: 'Расширительный бак',
    category: 'storage',
    icon: 'expansion-tank',
    defaultSize: { width: 78, height: 104 },
    ports: [
      { id: 'connection', label: 'Подключение', side: 'bottom', direction: 'bottom', x: 39, y: 104, kind: 'inlet' },
    ],
  },
  {
    type: 'circulation-pump',
    label: 'Циркуляционный насос',
    category: 'pumps',
    icon: 'pump',
    defaultSize: { width: 74, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet' },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 74, y: 37, kind: 'outlet' },
    ],
  },
  {
    type: 'ball-valve',
    label: 'Шаровой кран',
    category: 'valves',
    icon: 'ball-valve',
    defaultSize: { width: 74, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet' },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 74, y: 37, kind: 'outlet' },
    ],
  },
  {
    type: 'balancing-valve',
    label: 'Балансировочный вентиль',
    category: 'valves',
    icon: 'balancing-valve',
    defaultSize: { width: 74, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet' },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 74, y: 37, kind: 'outlet' },
    ],
  },
  {
    type: 'check-valve',
    label: 'Обратный клапан',
    category: 'valves',
    icon: 'check-valve',
    defaultSize: { width: 76, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet' },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 76, y: 37, kind: 'outlet' },
    ],
  },
  {
    type: 'pressure-reducer',
    label: 'Редуктор давления',
    category: 'valves',
    icon: 'pressure-reducer',
    defaultSize: { width: 76, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet', allowedLineTypes: ['pipe_cold_water'] },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 76, y: 37, kind: 'outlet', allowedLineTypes: ['pipe_cold_water'] },
    ],
  },
  {
    type: 'safety-valve',
    label: 'Предохранительный клапан',
    category: 'valves',
    icon: 'safety-valve',
    defaultSize: { width: 74, height: 80 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'bottom', direction: 'bottom', x: 31, y: 80, kind: 'inlet' },
      { id: 'discharge', label: 'Сброс', side: 'right', direction: 'right', x: 74, y: 50, kind: 'drain', allowedLineTypes: ['pipe_drain'] },
    ],
  },
  {
    type: 'filter',
    label: 'Фильтр',
    category: 'treatment',
    icon: 'filter',
    defaultSize: { width: 72, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet', allowedLineTypes: ['pipe_cold_water'] },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 72, y: 37, kind: 'outlet', allowedLineTypes: ['pipe_cold_water'] },
      { id: 'drain', label: 'Сброс', side: 'bottom', direction: 'bottom', x: 36, y: 74, kind: 'drain', allowedLineTypes: ['pipe_drain'] },
    ],
  },
  {
    type: 'water-meter',
    label: 'Счётчик воды',
    category: 'treatment',
    icon: 'water-meter',
    defaultSize: { width: 82, height: 74 },
    ports: [
      { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 37, kind: 'inlet', allowedLineTypes: ['pipe_cold_water'] },
      { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 82, y: 37, kind: 'outlet', allowedLineTypes: ['pipe_cold_water'] },
    ],
  },
  {
    type: 'pressure-gauge',
    label: 'Манометр',
    category: 'instruments',
    icon: 'pressure-gauge',
    defaultSize: { width: 58, height: 74 },
    ports: [
      { id: 'tap', label: 'Отбор давления', side: 'bottom', direction: 'bottom', x: 29, y: 74, kind: 'sensor' },
    ],
  },
  {
    type: 'junction',
    label: 'Узел (ответвление)',
    category: 'connections',
    icon: 'junction',
    defaultSize: { width: 18, height: 18 },
    ports: [
      { id: 'top', label: 'Узел', side: 'top', direction: 'top', x: 9, y: 0, kind: 'junction' },
      { id: 'right', label: 'Узел', side: 'right', direction: 'right', x: 18, y: 9, kind: 'junction' },
      { id: 'bottom', label: 'Узел', side: 'bottom', direction: 'bottom', x: 9, y: 18, kind: 'junction' },
      { id: 'left', label: 'Узел', side: 'left', direction: 'left', x: 0, y: 9, kind: 'junction' },
    ],
  },
  {
    type: 'water-connection',
    label: 'Точка подключения воды',
    category: 'connections',
    icon: 'water-connection',
    defaultSize: { width: 84, height: 84 },
    ports: [
      { id: 'outlet', label: 'Выход воды', side: 'right', direction: 'right', x: 84, y: 42, kind: 'outlet', allowedLineTypes: ['pipe_cold_water'] },
    ],
  },
];

/** Fast lookup by element type. */
export const elementCatalogMap: Record<string, HydraulicElementDef> =
  Object.fromEntries(elementCatalog.map((e) => [e.type, e]));

export function getElementDef(type: string): HydraulicElementDef | undefined {
  return elementCatalogMap[type];
}
