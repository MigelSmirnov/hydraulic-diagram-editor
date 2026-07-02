import type { ReactNode } from 'react';

interface PropertyRowProps {
  label: string;
  value: ReactNode;
  mono?: boolean;
}

/** Generic label/value row. Reusable UI, no hydraulic knowledge. */
export function PropertyRow({ label, value, mono }: PropertyRowProps) {
  return (
    <div className="property-row">
      <span className="property-row__label">{label}</span>
      <span className={`property-row__value${mono ? ' is-mono' : ''}`}>{value}</span>
    </div>
  );
}
