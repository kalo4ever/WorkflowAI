import { cx } from 'class-variance-authority';
import { TableView } from '@/components/ui/TableView';
import { TableViewHeaderEntry } from '@/components/ui/TableView';

type PlaceholderRectangleProps = {
  className?: string;
};

function PlaceholderRectangle(props: PlaceholderRectangleProps) {
  const { className } = props;
  return (
    <div
      className={cx(
        'h-3 bg-gradient-to-r from-gray-100 to-gray-200 rounded-[2px]',
        className
      )}
    />
  );
}

function LoadingTaskRow() {
  return (
    <div className='flex flex-row w-full h-[48px] px-2.5 items-center border-b border-gray-200'>
      <div className='flex flex-row w-full h-full items-center animate-pulse justify-between'>
        <div className='flex flex-row gap-2'>
          <PlaceholderRectangle className='w-3' />
          <PlaceholderRectangle className='w-[140px]' />
        </div>
        <div className='flex flex-row gap-4 pr-2'>
          <PlaceholderRectangle className='w-[32px]' />
          <PlaceholderRectangle className='w-[32px]' />
        </div>
      </div>
    </div>
  );
}

export function LoadingTasksTable() {
  return (
    <TableView
      headers={
        <>
          <TableViewHeaderEntry title='AI Agent' className='pl-2 flex-1' />
          <TableViewHeaderEntry title='Runs' className='w-[48px]' />
          <TableViewHeaderEntry title='Cost' className='w-[48px]' />
        </>
      }
    >
      {Array.from({ length: 10 }).map((_, index) => (
        <div key={index} style={{ opacity: 1 - index / 9 }}>
          <LoadingTaskRow key={index} />
        </div>
      ))}
    </TableView>
  );
}
