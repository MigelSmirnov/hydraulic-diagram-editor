import type { SVGProps } from 'react';

// Ball valve — bow-tie body with a stem/handle.
export function BallValveIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="10" y2="24" />
      <line x1="38" y1="24" x2="48" y2="24" />
      <path d="M10 16 L10 32 L24 24 Z" />
      <path d="M38 16 L38 32 L24 24 Z" />
      <line x1="24" y1="24" x2="24" y2="12" />
      <line x1="18" y1="12" x2="30" y2="12" />
    </svg>
  );
}
