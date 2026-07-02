import type { SVGProps } from 'react';

// Circulation pump — circle with an impeller arrow.
export function PumpIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="9" y2="24" />
      <line x1="39" y1="24" x2="48" y2="24" />
      <circle cx="24" cy="24" r="15" />
      <path d="M24 24 L34 19" />
      <path d="M24 24 L24 12" />
      <path d="M24 24 L14 30" />
    </svg>
  );
}
