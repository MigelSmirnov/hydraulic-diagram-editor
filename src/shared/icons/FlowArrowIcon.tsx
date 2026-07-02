import type { SVGProps } from 'react';

// Flow-direction arrow — a standalone marker. Filled with currentColor so it
// inherits the tint of its node's line type; rotate the node to aim it.
export function FlowArrowIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M8 24 L30 24" />
      <path d="M28 12 L44 24 L28 36 Z" fill="currentColor" stroke="none" />
    </svg>
  );
}
