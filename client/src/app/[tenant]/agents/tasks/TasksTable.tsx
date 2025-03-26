import { TableView } from '@/components/ui/TableView';
import { TenantID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { TaskRowContainer } from './TaskRow';
import { TasksTableHeaders } from './TasksTableHeaders';

type TasksTableProps = {
  tenant: TenantID;
  tasks: SerializableTask[];
  onTryInPlayground: (task: SerializableTask) => void;
  onViewRuns: (task: SerializableTask) => void;
  onViewCode: (task: SerializableTask) => void;
  onViewDeployments: (task: SerializableTask) => void;
};

export function TasksTable(props: TasksTableProps) {
  const { tasks, onTryInPlayground, onViewRuns, onViewCode, onViewDeployments, tenant } = props;

  return (
    <TableView headers={<TasksTableHeaders />}>
      {tasks.map((task) => (
        <TaskRowContainer
          tenant={tenant}
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
