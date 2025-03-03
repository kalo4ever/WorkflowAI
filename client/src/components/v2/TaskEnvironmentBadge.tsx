import { EnvironmentIcon } from '@/components/icons/EnvironmentIcon';
import { Badge } from '@/components/ui/Badge';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { getEnvironmentShorthandName } from '@/lib/versionUtils';
import { VersionEnvironment } from '@/types/workflowAI';

type TaskEnvironmentBadgeProps = {
  environment: VersionEnvironment | null | undefined;
  useShorthandName?: boolean;
  showIconOnly?: boolean;
};

export function TaskEnvironmentBadge(props: TaskEnvironmentBadgeProps) {
  const { environment, useShorthandName = false, showIconOnly = false } = props;

  if (!environment) {
    return null;
  }

  return (
    <SimpleTooltip
      content={
        showIconOnly ? (
          <div className='truncate capitalize'>{environment}</div>
        ) : undefined
      }
    >
      <Badge>
        <div className='flex items-center gap-1 max-w-[300px] font-lato'>
          <EnvironmentIcon environment={environment} />
          {!showIconOnly && (
            <div className='truncate capitalize'>
              {useShorthandName
                ? getEnvironmentShorthandName(environment)
                : environment}
            </div>
          )}
        </div>
      </Badge>
    </SimpleTooltip>
  );
}
