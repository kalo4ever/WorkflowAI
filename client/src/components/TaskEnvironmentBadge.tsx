import { getEnvironmentShorthandName } from '@/lib/versionUtils';
import { VersionEnvironment } from '@/types/workflowAI';
import { EnvironmentIcon } from './icons/EnvironmentIcon';
import { Badge } from './ui/Badge';

type TaskEnvironmentBadgeProps = {
  environment: VersionEnvironment | null | undefined;
  useShorthandName?: boolean;
  className?: string;
};

export function TaskEnvironmentBadge(props: TaskEnvironmentBadgeProps) {
  const { environment, useShorthandName = false, className } = props;

  if (!environment) {
    return null;
  }

  return (
    <Badge variant='default' className={className}>
      <div className='flex items-center gap-1 max-w-[300px]'>
        <EnvironmentIcon environment={environment} />
        <div className='truncate font-mono font-normal'>
          {useShorthandName ? getEnvironmentShorthandName(environment) : environment}
        </div>
      </div>
    </Badge>
  );
}
