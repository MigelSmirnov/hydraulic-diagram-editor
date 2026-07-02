import type { SVGProps } from 'react';

// Solar collector — panel with absorber grid.
export function SolarCollectorIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="6" y="10" width="36" height="24" rx="2" />
      <line x1="6" y1="18" x2="42" y2="18" />
      <line x1="6" y1="26" x2="42" y2="26" />
      <line x1="18" y1="10" x2="18" y2="34" />
      <line x1="30" y1="10" x2="30" y2="34" />
      <line x1="18" y1="34" x2="18" y2="48" />
      <line x1="30" y1="34" x2="30" y2="48" />
    </svg>
  );
}
