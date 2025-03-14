import { ListBarTree16Regular } from '@fluentui/react-icons';
import { TaskActivityIndicator } from '@/components/TaskIterationBadge/TaskRunsActivityIndicator';
import { formatFractionalCurrency } from '@/lib/formatters/numberFormatters';
import { SerializableTask } from '@/types/workflowAI';
import { TaskTooltip } from './TaskTooltip';

type TaskRowProps = {
  task: SerializableTask;
  onTryInPlayground: (task: SerializableTask) => void;
  onViewRuns: (task: SerializableTask) => void;
  onViewCode: (task: SerializableTask) => void;
  onViewDeployments: (task: SerializableTask) => void;
};

export function TaskRow(props: TaskRowProps) {
  const { task, onTryInPlayground, onViewRuns, onViewCode, onViewDeployments } =
    props;

  const runCount = task.run_count;
  const cost = task.average_cost_usd;
  const name = task.name.length === 0 ? task.id : task.name;
  const formattedCost = formatFractionalCurrency(cost);

  return (
    <TaskTooltip
      onTryInPlayground={() => onTryInPlayground(task)}
      onViewRuns={() => onViewRuns(task)}
      onViewCode={() => onViewCode(task)}
      onViewDeployments={() => onViewDeployments(task)}
    >
      <div
        onClick={() => onTryInPlayground(task)}
        className='flex flex-row items-center justify-center cursor-pointer min-h-[44px] rounded-[2px] hover:bg-gray-100'
      >
        <div className='pl-2 flex-1 font-medium text-gray-900 text-[13px] items-center flex flex-row gap-1.5'>
          <TaskActivityIndicator task={task} />
          <div>{name}</div>
        </div>
        <div className='w-[70px] font-normal text-gray-500 text-[13px]'>
          {runCount ? (
            <div className='flex items-center gap-1 whitespace-nowrap'>
              <ListBarTree16Regular />
              <div>{runCount}</div>
            </div>
          ) : (
            <div className='text-gray-700 text-base pl-2'>-</div>
          )}
        </div>
        <div className='w-[57px] font-normal text-gray-500 text-[13px]'>
          {cost ? (
            formattedCost
          ) : (
            <div className='text-gray-700 text-base pl-2'>-</div>
          )}
        </div>
      </div>
    </TaskTooltip>
  );
}
