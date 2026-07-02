import type { SVGProps } from 'react';

// Indirect boiler — insulated tank with an internal heat-exchanger coil.
export function BoilerIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="14" y="6" width="20" height="36" rx="6" />
      <line x1="0" y1="39" x2="14" y2="39" />
      <line x1="34" y1="9" x2="48" y2="9" />
      <line x1="0" y1="26" x2="14" y2="26" />
      <line x1="0" y1="35" x2="14" y2="35" />
      <line x1="24" y1="42" x2="24" y2="48" />
      <path d="M20 15c4 0 4 4 8 4s4 4 8 4" transform="translate(-4 0)" />
      <path d="M20 24c4 0 4 4 8 4" transform="translate(-4 0)" />
    </svg>
  );
}
