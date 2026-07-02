import type { SVGProps } from 'react';

// Water meter — inline housing with a round register dial.
export function WaterMeterIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="12" y2="24" />
      <line x1="36" y1="24" x2="48" y2="24" />
      <rect x="12" y="13" width="24" height="22" rx="3" />
      <circle cx="24" cy="24" r="6" />
      <line x1="24" y1="24" x2="24" y2="19" />
    </svg>
  );
}
