let seq = 0;

/** Generates a unique, human-scannable id (e.g. "pump-abc-3"). */
export function createId(prefix = 'id'): string {
  seq += 1;
  return `${prefix}-${Date.now().toString(36)}-${seq.toString(36)}`;
}
