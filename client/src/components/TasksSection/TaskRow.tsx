import { TaskActivityIndicator } from '@/components/TaskIterationBadge/TaskRunsActivityIndicator';
import { SerializableTask } from '@/types/workflowAI';

type TaskRowProps = {
  task: SerializableTask;
  onTryInPlayground: (task: SerializableTask) => void;
};

export function TaskRow(props: TaskRowProps) {
  const { task, onTryInPlayground } = props;

  const name = task.name.length === 0 ? task.id : task.name;

  return (
    <div
      className='px-2 font-normal text-gray-600 text-[13px] items-center flex flex-row gap-1.5 w-full py-2 cursor-pointer hover:bg-gray-100'
      onClick={() => onTryInPlayground(task)}
    >
      <TaskActivityIndicator task={task} />
      <div className='flex-1 truncate'>{name}</div>
    </div>
  );
}
