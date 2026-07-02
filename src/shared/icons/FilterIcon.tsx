import type { SVGProps } from 'react';

// Filter — housing with a cartridge / mesh inside.
export function FilterIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="15" y2="24" />
      <line x1="33" y1="24" x2="48" y2="24" />
      <rect x="15" y="12" width="18" height="22" rx="3" />
      <path d="M19 16 L29 30 M29 16 L19 30" />
      <path d="M24 34 L24 48" />
    </svg>
  );
}
