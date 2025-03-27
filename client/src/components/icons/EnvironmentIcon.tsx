import {
  Globe16Filled,
  Globe16Regular,
  RoadCone16Filled,
  RoadCone16Regular,
  Wrench16Filled,
  Wrench16Regular,
} from '@fluentui/react-icons';
import { VersionEnvironment } from '@/types/workflowAI';

type EnvironmentIconProps = {
  environment: VersionEnvironment | null | undefined;
  className?: string;
  filled?: boolean;
};

function iconForEnvironment(environment: VersionEnvironment | null | undefined, filled: boolean = false) {
  if (!environment) {
    return null;
  }

  switch (environment) {
    case 'dev':
      return filled ? Wrench16Filled : Wrench16Regular;
    case 'staging':
      return filled ? RoadCone16Filled : RoadCone16Regular;
    case 'production':
      return filled ? Globe16Filled : Globe16Regular;
  }
}

export function EnvironmentIcon(props: EnvironmentIconProps) {
  const { environment, className, filled } = props;

  const Icon = iconForEnvironment(environment, filled);

  if (!Icon) {
    return null;
  }

  return <Icon className={className} />;
}
