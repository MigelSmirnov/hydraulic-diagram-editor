// Domain model for the hydraulic diagram editor.
// These types are framework-agnostic where possible; React Flow specifics
// (Node/Edge) are only referenced in the store and utils.

export type ElementCategory =
  | 'solar'
  | 'storage'
  | 'pumps'
  | 'valves'
  | 'treatment'
  | 'instruments'
  | 'connections';

export interface CategoryDef {
  id: ElementCategory;
  label: string;
}

/** The four sides where a connection point (handle) can live. */
export type HandleId = 'top' | 'right' | 'bottom' | 'left';
export type PortDirection = HandleId;
export type PortKind =
  | 'inlet'
  | 'outlet'
  | 'solar_supply'
  | 'solar_return'
  | 'drain'
  | 'sensor'
  | 'junction';

export interface ElementSize {
  width: number;
  height: number;
}

export interface ElementPort {
  id: string;
  label: string;
  side: HandleId;
  direction: PortDirection;
  /** Local x coordinate inside the symbol bounds. */
  x: number;
  /** Local y coordinate inside the symbol bounds. */
  y: number;
  kind: PortKind;
  allowedLineTypes?: LineTypeId[];
  showLabel?: boolean;
}

/**
 * A single engineering symbol definition. Symbols are the atomic elements of
 * the diagram and live in elementCatalog.ts.
 */
export interface SymbolDef {
  /** Stable machine id, also used as the drag payload. */
  type: string;
  /** Human-readable name shown in the palette and on the node. */
  label: string;
  category: ElementCategory;
  /** Key into the icon registry (shared/icons). Kept as a string so the */
  /** catalog stays free of JSX / React imports. */
  icon: string;
  defaultSize: ElementSize;
  /** Connection ports in local symbol coordinates. */
  ports: ElementPort[];
  /**
   * When true, the symbol is tinted with its node's `lineType` colour instead
   * of the default icon colour — used for annotations like the flow arrow.
   */
  tintFromLineType?: boolean;
}

/** Existing name kept for current editor code. */
export type HydraulicElementDef = SymbolDef;

/** Data carried by every hydraulic node instance on the canvas. */
export interface HydraulicNodeData {
  /** Element type from the catalog. */
  type: string;
  label: string;
  rotation?: number;
  /** Line type whose colour tints the symbol (for `tintFromLineType` elements). */
  lineType?: string;
}

/** All line types the editor knows about. */
export type LineTypeCategory = 'water' | 'solar' | 'drain' | 'control';
export type LineVisualStyle = 'solid' | 'dashed' | 'dotted';

export type LineTypeId = string;

export interface LineTypeDef {
  id: LineTypeId;
  label: string;
  category: LineTypeCategory;
  visualStyle: LineVisualStyle;
  color: string;
  strokeWidth: number;
  dasharray?: string;
  description: string;
}

/** Data carried by every edge instance on the canvas. */
export interface HydraulicEdgeData {
  lineType?: string;
}

// ---- Templates -------------------------------------------------------------

export interface TemplateNode {
  id: string;
  /** Element type from the catalog. */
  type: string;
  position: { x: number; y: number };
  /** Optional label override; falls back to the catalog label. */
  label?: string;
}

export interface TemplateEdge {
  id: string;
  source: string;
  sourceHandle: string;
  target: string;
  targetHandle: string;
  lineType: LineTypeId;
}

export type AssemblyCategory =
  | 'cold_water_inlet'
  | 'water_treatment'
  | 'solar_pump_group'
  | 'boiler_safety_group'
  | 'boiler_group'
  | 'collector_group'
  | 'custom';

/**
 * Future Simulink-like assembly block. It is not a flat image: it exposes
 * external ports and contains an editable internal diagram.
 */
export interface AssemblyBlockDef {
  id: string;
  label: string;
  category: AssemblyCategory;
  externalPorts: ElementPort[];
  internalNodes: TemplateNode[];
  internalEdges: TemplateEdge[];
  defaultSize: ElementSize;
  description?: string;
}

export interface DiagramTemplate {
  id: string;
  name: string;
  description?: string;
  nodes: TemplateNode[];
  edges: TemplateEdge[];
}
