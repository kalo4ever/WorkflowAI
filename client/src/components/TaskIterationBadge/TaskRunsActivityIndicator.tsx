import { useMemo } from 'react';
import { isActiveTask } from '@/lib/taskUtils';
import { cn } from '@/lib/utils';
import { SerializableTask } from '@/types/workflowAI';
import { SimpleTooltip } from '../ui/Tooltip';

type TaskRunsActivityIndicatorProps = {
  isActive: boolean;
};

export function TaskRunsActivityIndicator(
  props: TaskRunsActivityIndicatorProps
) {
  const { isActive } = props;

  return (
    <div className='relative'>
      <div
        className={cn(
          'w-[6px] h-[6px] rounded-full',
          isActive
            ? 'bg-green-500 animate-[pulse-scale_2s_ease-in-out_infinite]'
            : 'bg-gray-300'
        )}
      />
      <div
        className={cn(
          'absolute top-[-3px] left-[-3px] w-[12px] h-[12px] rounded-full border',
          isActive
            ? 'border-green-500 animate-[pulse-scale_2s_ease-in-out_infinite]'
            : 'border-gray-300'
        )}
      />
    </div>
  );
}

type TaskActivityIndicatorProps = {
  task: SerializableTask;
};

export function TaskActivityIndicator(props: TaskActivityIndicatorProps) {
  const { task } = props;
  const isActive = useMemo(() => isActiveTask(task), [task]);

  return (
    <SimpleTooltip
      content={
        isActive
          ? `One or more versions of this AI agent have\nbeen recently run through your app`
          : null
      }
      tooltipClassName='whitespace-break-spaces text-center'
    >
      <div className='flex items-center justify-center h-4 w-4'>
        <TaskRunsActivityIndicator isActive={isActive} />
      </div>
    </SimpleTooltip>
  );
}

type TaskIterationActivityIndicatorProps = {
  height?: number;
};

export function TaskIterationActivityIndicator(
  props: TaskIterationActivityIndicatorProps
) {
  const { height } = props;

  return (
    <div
      className={cn(
        'flex items-center justify-center bg-gray-50 rounded-r-[2px] border border-gray-200 px-2',
        !!height ? `h-[${height}px]` : 'h-full'
      )}
    >
      <TaskRunsActivityIndicator isActive={true} />
    </div>
  );
}
