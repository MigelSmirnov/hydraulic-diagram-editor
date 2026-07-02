import type { SVGProps } from 'react';

// Water connection point — supply stub with a droplet.
export function WaterConnectionIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="24" cy="24" r="15" />
      <line x1="39" y1="24" x2="48" y2="24" />
      <path d="M24 14 C29 20 30 24 30 27 a6 6 0 0 1 -12 0 C18 24 19 20 24 14 Z" />
    </svg>
  );
}
