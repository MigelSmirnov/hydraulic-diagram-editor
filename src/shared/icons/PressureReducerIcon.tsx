import type { SVGProps } from 'react';

// Pressure reducer — bow-tie valve body with a diaphragm dome and adjuster on top.
export function PressureReducerIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="14" y2="24" />
      <line x1="34" y1="24" x2="48" y2="24" />
      <path d="M14 16 L14 32 L34 16 L34 32 Z" />
      <path d="M17 16 Q24 2 31 16" />
      <line x1="24" y1="7" x2="24" y2="3" />
      <line x1="19" y1="3" x2="29" y2="3" />
    </svg>
  );
}
