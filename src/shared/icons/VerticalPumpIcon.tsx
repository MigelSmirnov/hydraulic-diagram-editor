import type { SVGProps } from 'react';

// Vertical pump — circle with upward flow direction.
export function VerticalPumpIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <line x1="24" y1="0" x2="24" y2="8" />
      <line x1="24" y1="40" x2="24" y2="48" />
      <circle cx="24" cy="24" r="16" />
      <path d="M24 10 L15 25 H33 Z" fill="currentColor" stroke="none" />
    </svg>
  );
}
