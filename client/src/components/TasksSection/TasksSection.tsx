import { Search16Regular } from '@fluentui/react-icons';
import { useState } from 'react';
import { useCallback } from 'react';
import { WorkflowAIIcon } from '@/components/Logos/WorkflowAIIcon';
import { Input } from '@/components/ui/Input';
import { RecentTasksEntry } from '@/store/recentTasks';
import { TaskSchemaID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { TasksSectionContent } from './TasksSectionContent';

type TasksSectionProps = {
  tasks: SerializableTask[];
  recentTasksEntries: RecentTasksEntry[];
  isInitialized: boolean;
  onTryInPlayground: (task: SerializableTask, taskSchemaId?: TaskSchemaID) => void;
};

export function TasksSection(props: TasksSectionProps) {
  const { tasks, recentTasksEntries, isInitialized, onTryInPlayground } = props;

  const [searchText, setSearchText] = useState('');

  const handleSearchTextChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(e.target.value);
  }, []);

  return (
    <>
      <div className='flex items-center gap-2 px-[10px] py-[10px] flex-shrink-0'>
        <WorkflowAIIcon ratio={1.3} />
        <span className='font-sans text-[20px] bg-gradient-to-r from-[#8759E3] to-[#4235F8] text-transparent bg-clip-text'>
          <span className='font-semibold'>Workflow</span>
          <span className='font-normal'>AI</span>
        </span>
      </div>
      <div className='flex flex-row gap-1.5 pl-[10px] h-[48px] items-center justify-center bg-gray-50 border-b border-t border-gray-100 flex-shrink-0'>
        <Search16Regular className='text-gray-500' />
        <Input
          placeholder='Search AI Agents...'
          value={searchText}
          onChange={handleSearchTextChange}
          className='border-none bg-transparent focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 h-full placeholder:text-gray-400 text-[13px] placeholder:font-normal text-gray-900 px-0'
        />
      </div>
      <TasksSectionContent
        tasks={tasks}
        recentTasksEntries={recentTasksEntries}
        isInitialized={isInitialized}
        searchText={searchText}
        onTryInPlayground={onTryInPlayground}
      />
    </>
  );
}
