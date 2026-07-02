import type { SVGProps } from 'react';

// Safety / relief valve — angle body with a spring on top: inlet at the
// bottom, discharge to the right.
export function SafetyValveIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="20" cy="30" r="9" />
      <line x1="20" y1="39" x2="20" y2="48" />
      <line x1="29" y1="30" x2="48" y2="30" />
      <line x1="20" y1="21" x2="20" y2="17" />
      <path d="M15 16 L25 13 L15 10 L25 7" />
      <line x1="20" y1="6" x2="20" y2="4" />
      <line x1="15" y1="4" x2="25" y2="4" />
    </svg>
  );
}
