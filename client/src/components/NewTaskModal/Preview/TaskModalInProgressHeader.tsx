import { Loader2 } from 'lucide-react';

type TaskModalInProgressHeaderProps = {
  title: string;
  inProgress: boolean;
  inProgressText: string;
};

export function TaskModalInProgressHeader(props: TaskModalInProgressHeaderProps) {
  const { title, inProgress, inProgressText } = props;

  return (
    <div className='flex flex-row pl-4 gap-4 h-[64px] flex-shrink-0 items-center'>
      <div className='text-gray-700 text-base font-semibold'>{title}</div>
      {inProgress && (
        <div className='flex flex-row gap-2 items-center'>
          <Loader2 className='w-4 h-4 animate-spin text-gray-400' />
          <div className='text-gray-400 text-[13px] font-medium'>{inProgressText}</div>
        </div>
      )}
    </div>
  );
}
