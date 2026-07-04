import type { SVGProps } from 'react';

// Flange — pipe continuation with two parallel plates, like a capacitor symbol.
export function FlangeIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="21" y2="24" />
      <line x1="27" y1="24" x2="48" y2="24" />
      <line x1="21" y1="12" x2="21" y2="36" />
      <line x1="27" y1="12" x2="27" y2="36" />
    </svg>
  );
}
