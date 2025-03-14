import { TableView } from '@/components/ui/TableView';
import { TableViewHeaderEntry } from '@/components/ui/TableView';
import { SerializableTask } from '@/types/workflowAI';
import { TaskRow } from './TaskRow';

type TasksTableProps = {
  tasks: SerializableTask[];
  onTryInPlayground: (task: SerializableTask) => void;
  onViewRuns: (task: SerializableTask) => void;
  onViewCode: (task: SerializableTask) => void;
  onViewDeployments: (task: SerializableTask) => void;
};

export function TasksTable(props: TasksTableProps) {
  const {
    tasks,
    onTryInPlayground,
    onViewRuns,
    onViewCode,
    onViewDeployments,
  } = props;

  return (
    <TableView
      headers={
        <>
          <TableViewHeaderEntry title='AI agent' className='pl-2 flex-1' />
          <TableViewHeaderEntry title='Runs' className='w-[70px]' />
          <TableViewHeaderEntry title='Cost' className='w-[57px]' />
        </>
      }
    >
      {tasks.map((task) => (
        <TaskRow
          key={task.id}
          task={task}
          onTryInPlayground={() => onTryInPlayground(task)}
          onViewRuns={() => onViewRuns(task)}
          onViewCode={() => onViewCode(task)}
          onViewDeployments={() => onViewDeployments(task)}
        />
      ))}
    </TableView>
  );
}
