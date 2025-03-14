import { FluentIcon } from '@fluentui/react-icons';
import { cn } from '@/lib/utils';

type TaskVersionsListSectionHeaderProps = {
  icon: FluentIcon | undefined;
  title: string;
};

export function TaskVersionsListSectionHeader(
  props: TaskVersionsListSectionHeaderProps
) {
  const { icon: Icon, title } = props;
  return (
    <div
      className={cn(
        'flex gap-2 px-4 py-3.5 border-t first:border-t-0 border-b border-dashed border-gray-200 items-center text-gray-500 font-lato'
      )}
    >
      {Icon && <Icon className='w-5 h-5 text-gray-500' />}
      <div className='text-base font-semibold text-gray-700'>{title}</div>
    </div>
  );
}
