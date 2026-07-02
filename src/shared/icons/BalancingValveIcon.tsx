import type { SVGProps } from 'react';

// Balancing valve — same bow-tie body as the ball valve, but the T-handle is
// moved off the centre apex to the midpoint of the left triangle's upper edge
// and tilted perpendicular to that edge.
export function BalancingValveIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="10" y2="24" />
      <line x1="38" y1="24" x2="48" y2="24" />
      <path d="M10 16 L10 32 L24 24 Z" />
      <path d="M38 16 L38 32 L24 24 Z" />
      <line x1="17" y1="20" x2="23" y2="10" />
      <line x1="18" y1="7" x2="28" y2="13" />
    </svg>
  );
}
