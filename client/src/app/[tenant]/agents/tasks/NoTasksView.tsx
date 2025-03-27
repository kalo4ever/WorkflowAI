import { AppsAddIn24Regular } from '@fluentui/react-icons';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/Button';

type NoTasksViewProps = {
  onNewTask: () => void;
};

export function NoTasksView(props: NoTasksViewProps) {
  const { onNewTask } = props;

  return (
    <div className='flex flex-col items-center'>
      <div className='flex items-center justify-center w-[56px] h-[56px] rounded-full bg-gradient-image mb-4'>
        <AppsAddIn24Regular className='text-white' />
      </div>
      <div className='text-gray-700 text-[14px] font-semibold'>No AI agents Yet</div>
      <Button
        className='w-full mt-4'
        variant='newDesignIndigo'
        icon={<Plus className='h-4 w-4' strokeWidth={2} />}
        onClick={onNewTask}
      >
        New
      </Button>
    </div>
  );
}
