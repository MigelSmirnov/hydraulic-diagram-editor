import type { FC, SVGProps } from 'react';
import { SolarCollectorIcon } from './SolarCollectorIcon';
import { BoilerIcon } from './BoilerIcon';
import { ExpansionTankIcon } from './ExpansionTankIcon';
import { PumpIcon } from './PumpIcon';
import { VerticalPumpIcon } from './VerticalPumpIcon';
import { BallValveIcon } from './BallValveIcon';
import { ThreeWayActuatedValveIcon } from './ThreeWayActuatedValveIcon';
import { FlangeIcon } from './FlangeIcon';
import { FilterIcon } from './FilterIcon';
import { WaterConnectionIcon } from './WaterConnectionIcon';
import { CheckValveIcon } from './CheckValveIcon';
import { SafetyValveIcon } from './SafetyValveIcon';
import { PressureReducerIcon } from './PressureReducerIcon';
import { WaterMeterIcon } from './WaterMeterIcon';
import { PressureGaugeIcon } from './PressureGaugeIcon';
import { BalancingValveIcon } from './BalancingValveIcon';
import { JunctionIcon } from './JunctionIcon';
import { FlowArrowIcon } from './FlowArrowIcon';

export type IconComponent = FC<SVGProps<SVGSVGElement>>;

/**
 * Icon registry: maps the `icon` key from elementCatalog to a pure SVG
 * component. Icons live here and know nothing about hydraulic logic.
 */
export const iconRegistry: Record<string, IconComponent> = {
  'solar-collector': SolarCollectorIcon,
  'boiler': BoilerIcon,
  'expansion-tank': ExpansionTankIcon,
  'pump': PumpIcon,
  'vertical-pump': VerticalPumpIcon,
  'ball-valve': BallValveIcon,
  'three-way-actuated-valve': ThreeWayActuatedValveIcon,
  'flange': FlangeIcon,
  'filter': FilterIcon,
  'water-connection': WaterConnectionIcon,
  'check-valve': CheckValveIcon,
  'safety-valve': SafetyValveIcon,
  'pressure-reducer': PressureReducerIcon,
  'water-meter': WaterMeterIcon,
  'pressure-gauge': PressureGaugeIcon,
  'balancing-valve': BalancingValveIcon,
  'junction': JunctionIcon,
  'flow-arrow': FlowArrowIcon,
};

export function getIcon(key: string): IconComponent | undefined {
  return iconRegistry[key];
}
