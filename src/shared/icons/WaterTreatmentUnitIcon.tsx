import type { SVGProps } from 'react';

// Water treatment unit — serviceable treatment block with inlet, outlet and drain.
export function WaterTreatmentUnitIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 64 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="0" y1="24" x2="12" y2="24" />
      <line x1="52" y1="24" x2="64" y2="24" />
      <rect x="12" y="8" width="40" height="32" rx="4" />
      <path d="M20 15 H44" />
      <path d="M20 24 H44" />
      <path d="M20 33 H44" />
      <path d="M32 40 V48" />
      <path d="M26 44 H38" />
      <circle cx="22" cy="24" r="2" />
      <circle cx="32" cy="24" r="2" />
      <circle cx="42" cy="24" r="2" />
    </svg>
  );
}
