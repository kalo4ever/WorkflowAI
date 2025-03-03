import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { TaskSchemaID } from '@/types/aliases';
import { TaskSchemaBadge } from './TaskSchemaBadge';

type TaskSchemaBadgeContainerProps = {
  schemaId: TaskSchemaID;
  isActive?: boolean;
};

export function TaskSchemaBadgeContainer(props: TaskSchemaBadgeContainerProps) {
  const { schemaId, isActive = false } = props;

  const { tenant, taskId } = useTaskSchemaParams();

  return (
    <TaskSchemaBadge
      tenant={tenant}
      taskId={taskId}
      schemaId={schemaId}
      isActive={isActive}
    />
  );
}
