import type { SVGProps } from 'react';

// Expansion tank — vertical vessel with a membrane line.
export function ExpansionTankIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="16" y="8" width="16" height="30" rx="8" />
      <line x1="16" y1="22" x2="32" y2="22" />
      <line x1="24" y1="38" x2="24" y2="48" />
    </svg>
  );
}
