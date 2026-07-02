import type { SVGProps } from 'react';

// Check valve — valve bow-tie of two triangles; one is filled to mark the
// allowed flow direction.
export function CheckValveIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="10" y2="24" />
      <line x1="38" y1="24" x2="48" y2="24" />
      <path d="M10 15 L10 33 L24 24 Z" fill="currentColor" />
      <path d="M38 15 L38 33 L24 24 Z" />
    </svg>
  );
}
