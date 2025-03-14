import { Search32Regular } from '@fluentui/react-icons';

type TaskRunEmptyViewProps = {
  title: string;
  subtitle: string;
};

export function TaskRunEmptyView(props: TaskRunEmptyViewProps) {
  const { title, subtitle } = props;
  return (
    <div className='flex flex-col items-center justify-center h-full w-full mb-8'>
      <div className='flex items-center justify-center w-[64px] h-[64px] rounded-full bg-gradient-image mb-6'>
        <Search32Regular className='text-white' />
      </div>
      <div className='text-gray-700 text-[14px] font-semibold'>{title}</div>
      <div className='text-gray-500 text-[14px] font-normal'>{subtitle}</div>
    </div>
  );
}
