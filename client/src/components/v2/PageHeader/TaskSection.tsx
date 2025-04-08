import { ChevronUpDownFilled } from '@fluentui/react-icons';
import { cn } from '@/lib/utils';
import { SerializableTask } from '@/types/workflowAI';

type TaskSectionProps = {
  task: SerializableTask;
  isSelected: boolean;
  organizationName: string | undefined;
};

export function TaskSection(props: TaskSectionProps) {
  const { task, isSelected, organizationName } = props;

  const taskName = task?.name;
  const isPublic = task?.is_public === true;

  return (
    <div className='flex flex-row items-center'>
      <div
        className={cn(
          'flex flex-row py-1.5 pl-3 pr-2.5 cursor-pointer items-center border border-gray-200/50 rounded-[2px]',
          isSelected
            ? 'border-gray-300 bg-gray-100 shadow-inner'
            : 'hover:border-gray-300 hover:bg-white/60 hover:shadow-sm'
        )}
      >
        <div className='text-[13px] font-normal text-gray-800'>
          {!!organizationName ? `${organizationName}/${taskName}` : taskName}
        </div>
        <div className='ml-2 text-[13px] font-medium text-yellow-700 bg-orange-50 border-orange-200 border rounded-[2px] px-1.5 py-0.5'>
          {isPublic ? 'Public' : 'Private'}
        </div>
        <ChevronUpDownFilled className='ml-2 h-4 w-4 shrink-0 text-[14px] text-gray-500' />
      </div>
      <div className='ml-3 text-[14px] font-semibold text-gray-400'>/</div>
    </div>
  );
}
