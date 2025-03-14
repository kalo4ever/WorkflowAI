import { Loader2 } from 'lucide-react';
import { RecentTasksEntry } from '@/store/recentTasks';
import { TaskSchemaID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { RecentTasksSectionContent } from './RecentTasksSectionContent';
import { SearchTasksSectionContent } from './SearchTasksSectionContent';

type TasksSectionContentProps = {
  tasks: SerializableTask[];
  recentTasksEntries: RecentTasksEntry[];
  isInitialized: boolean;
  searchText: string | undefined;
  onTryInPlayground: (
    task: SerializableTask,
    taskSchemaId?: TaskSchemaID
  ) => void;
};

export function TasksSectionContent(props: TasksSectionContentProps) {
  const {
    tasks,
    recentTasksEntries,
    isInitialized,
    searchText,
    onTryInPlayground,
  } = props;

  if (!isInitialized) {
    return (
      <div className='flex h-full w-full items-center justify-center'>
        <Loader2 className='h-6 w-6 animate-spin text-gray-300' />
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className='flex text-[12px] h-full w-full items-center justify-center text-gray-500'>
        No AI Agents Yet
      </div>
    );
  }

  if (searchText === undefined || searchText === '') {
    return (
      <RecentTasksSectionContent
        tasks={tasks}
        recentTasksEntries={recentTasksEntries}
        onTryInPlayground={onTryInPlayground}
      />
    );
  }

  return (
    <SearchTasksSectionContent
      tasks={tasks}
      searchText={searchText}
      onTryInPlayground={onTryInPlayground}
    />
  );
}
