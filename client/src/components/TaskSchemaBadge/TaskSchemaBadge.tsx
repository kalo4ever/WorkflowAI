import { cn } from '@/lib/utils';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { TaskStats } from '../TaskIterationBadge/TaskIterationStats';
import { TaskIterationActivityIndicator } from '../TaskIterationBadge/TaskRunsActivityIndicator';
import { SimpleTooltip } from '../ui/Tooltip';

type TaskSchemaBadgeProps = {
  tenant: TenantID;
  taskId: TaskID;
  schemaId: TaskSchemaID;
  isActive?: boolean;
};

export function TaskSchemaBadge(props: TaskSchemaBadgeProps) {
  const { tenant, taskId, schemaId, isActive = false } = props;
  return (
    <div className='flex items-center'>
      <div
        className={cn(
          'flex text-ellipsis whitespace-nowrap h-[24px] items-center justify-center text-gray-700 text-[13px] font-medium bg-gray-200 px-1.5',
          isActive ? 'rounded-l-[2px]' : 'rounded-[2px]'
        )}
      >
        #{schemaId}
      </div>

      {isActive && (
        <SimpleTooltip content={<TaskStats tenant={tenant} taskSchemaId={schemaId} taskId={taskId} />} side='top'>
          <div>
            <TaskIterationActivityIndicator height={24} />
          </div>
        </SimpleTooltip>
      )}
    </div>
  );
}
