import type { AssemblyBlockDef } from './types';

/**
 * ASSEMBLY CATALOG — future source of truth for Simulink-like assembly blocks.
 *
 * Assembly blocks are composed of internal symbols and edges. They are not
 * rendered as flat images: each block declares external ports and an internal
 * diagram that can later be expanded and edited.
 */
export const assemblyCatalog: AssemblyBlockDef[] = [];

export const assemblyCatalogMap: Record<string, AssemblyBlockDef> =
  Object.fromEntries(assemblyCatalog.map((block) => [block.id, block]));

export function getAssemblyBlockDef(id: string): AssemblyBlockDef | undefined {
  return assemblyCatalogMap[id];
}
