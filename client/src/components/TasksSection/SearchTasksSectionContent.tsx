import { useMemo } from 'react';
import { filterTasks, sortTasks } from '@/app/[tenant]/agents/tasks/utils';
import { SerializableTask } from '@/types/workflowAI';
import { TaskRow } from './TaskRow';

type SearchTasksSectionContentProps = {
  tasks: SerializableTask[];
  searchText: string;
  onTryInPlayground: (task: SerializableTask) => void;
};

export function SearchTasksSectionContent(
  props: SearchTasksSectionContentProps
) {
  const { tasks, searchText, onTryInPlayground } = props;

  const filteredTasks = useMemo(() => {
    const sortedTasks = sortTasks(tasks);
    const filteredTasks = filterTasks(sortedTasks, searchText);
    return filteredTasks;
  }, [tasks, searchText]);

  return (
    <div className='flex flex-col h-full w-full pt-3 overflow-y-auto'>
      {filteredTasks.map((task) => (
        <TaskRow
          key={task.id}
          task={task}
          onTryInPlayground={onTryInPlayground}
        />
      ))}
    </div>
  );
}
