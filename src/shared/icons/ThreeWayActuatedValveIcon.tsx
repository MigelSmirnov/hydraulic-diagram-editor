import type { SVGProps } from 'react';

// Three-way valve with an actuator above the valve body.
export function ThreeWayActuatedValveIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 74 92" fill="none" stroke="currentColor" strokeWidth={3}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="56" x2="16" y2="56" />
      <line x1="58" y1="56" x2="74" y2="56" />
      <line x1="37" y1="76" x2="37" y2="92" />

      <path d="M16 40 L16 72 L37 56 Z" />
      <path d="M58 40 L58 72 L37 56 Z" />
      <path d="M21 76 L53 76 L37 56 Z" />

      <line x1="37" y1="56" x2="37" y2="36" />
      <circle cx="37" cy="19" r="17" />
      <path d="M28 18 C28 12 36 10 39 15 C42 20 48 17 47 11" />
    </svg>
  );
}
