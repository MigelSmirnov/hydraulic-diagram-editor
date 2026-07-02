import type { SVGProps } from 'react';

// Pressure gauge — round dial with a needle and a stem down to the tapping point.
export function PressureGaugeIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={2}
      strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="24" cy="18" r="14" />
      <line x1="24" y1="18" x2="33" y2="10" />
      <circle cx="24" cy="18" r="1.6" fill="currentColor" stroke="none" />
      <line x1="24" y1="32" x2="24" y2="48" />
    </svg>
  );
}
