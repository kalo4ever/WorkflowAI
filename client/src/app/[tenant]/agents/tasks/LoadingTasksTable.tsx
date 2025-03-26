import { cx } from 'class-variance-authority';
import { TableView } from '@/components/ui/TableView';
import { TasksTableHeaders } from './TasksTableHeaders';

type PlaceholderRectangleProps = {
  className?: string;
};

function PlaceholderRectangle(props: PlaceholderRectangleProps) {
  const { className } = props;
  return <div className={cx('h-3 bg-gradient-to-r from-gray-100 to-gray-200 rounded-[2px]', className)} />;
}

function LoadingTaskRow() {
  return (
    <div className='flex flex-row w-full h-[48px] px-2.5 items-center border-b border-gray-200'>
      <div className='flex flex-row w-full h-full items-center animate-pulse gap-2'>
        <PlaceholderRectangle className='w-3' />
        <PlaceholderRectangle className='w-[140px] mr-auto' />
        <PlaceholderRectangle className='w-[100px]' />
        <PlaceholderRectangle className='w-[57px]' />
      </div>
    </div>
  );
}

export function LoadingTasksTable() {
  return (
    <TableView headers={<TasksTableHeaders />}>
      {Array.from({ length: 10 }).map((_, index) => (
        <div key={index} style={{ opacity: 1 - index / 9 }}>
          <LoadingTaskRow key={index} />
        </div>
      ))}
    </TableView>
  );
}
