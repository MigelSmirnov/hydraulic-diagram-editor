import type { SVGProps } from 'react';

// Junction — a plain filled dot used as a branch / tee point. It fills the box
// so pipes ending at the edge ports meet the dot exactly.
export function JunctionIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="24" cy="24" r="21" fill="currentColor" stroke="none" />
    </svg>
  );
}
