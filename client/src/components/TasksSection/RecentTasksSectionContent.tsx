import { useCallback, useMemo } from 'react';
import { getNewestSchemaId, getVisibleSchemaIds } from '@/lib/taskUtils';
import { RecentTasksEntry } from '@/store/recentTasks';
import { TaskSchemaID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { TaskRow } from './TaskRow';

type RecentTasksSectionContentProps = {
  tasks: SerializableTask[];
  recentTasksEntries: RecentTasksEntry[];
  onTryInPlayground: (
    task: SerializableTask,
    taskSchemaId?: TaskSchemaID
  ) => void;
};

export function RecentTasksSectionContent(
  props: RecentTasksSectionContentProps
) {
  const { tasks, recentTasksEntries, onTryInPlayground } = props;

  const onTryInPlaygroundWithoutSchemaId = useCallback(
    (task: SerializableTask) => {
      const entry = recentTasksEntries.find(
        (entry) => entry.taskId === task.id
      );

      const visibleSchemaIds = getVisibleSchemaIds(task);
      const isVisible = visibleSchemaIds.some(
        (schemaId) => schemaId === entry?.taskSchemaId
      );

      if (isVisible) {
        onTryInPlayground(task, entry?.taskSchemaId);
        return;
      }

      const newestSchemaId = getNewestSchemaId(task);
      onTryInPlayground(task, newestSchemaId);
    },
    [onTryInPlayground, recentTasksEntries]
  );

  const recentTasks = useMemo(() => {
    const result = recentTasksEntries.map((entry) => {
      const task = tasks.find((task) => task.id === entry.taskId);
      return task;
    });
    return result.filter((task): task is SerializableTask => !!task);
  }, [tasks, recentTasksEntries]);

  if (recentTasks.length === 0) {
    return <div className='flex flex-col h-full w-full overflow-y-auto' />;
  }

  return (
    <>
      <div className='text-[12px] text-indigo-700 font-semibold py-2 px-2.5 border-b border-t border-gray-100 mt-3'>
        RECENTLY VIEWED
      </div>
      <div className='flex flex-col h-full w-full overflow-y-auto'>
        {recentTasks.map((task) => (
          <TaskRow
            key={task.id}
            task={task}
            onTryInPlayground={onTryInPlaygroundWithoutSchemaId}
          />
        ))}
      </div>
    </>
  );
}
