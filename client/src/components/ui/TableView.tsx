import { ChevronUpDown16Regular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';

type TableViewHeaderEntryProps = {
  title: string;
  onClick?: () => void;
  className?: string;
};

export function TableViewHeaderEntry(props: TableViewHeaderEntryProps) {
  const { title, onClick, className } = props;
  return (
    <div
      className={cx(
        'flex flex-row gap-0.5 text-gray-900 font-lato text-[13px] font-medium py-3 items-center',
        !!onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {title}
      {!!onClick && <ChevronUpDown16Regular className='text-gray-500' />}
    </div>
  );
}

type TableViewProps = {
  maxContentHeight?: number;
  headers: React.ReactNode;
  children: React.ReactNode;
};

export function TableView(props: TableViewProps) {
  const { headers, children, maxContentHeight } = props;
  return (
    <div className='flex flex-col w-full border border-gray-200 rounded-[2px] bg-gradient-to-b from-white/50 to-white/0'>
      <div className='flex flex-col w-full overflow-x-auto'>
        <div className='flex w-full px-2'>
          <div className='flex flex-row w-full border-b border-gray-200'>
            {headers}
          </div>
        </div>

        <div
          className={cx(
            'flex flex-col w-full overflow-y-auto overflow-x-clip pb-2 px-2',
            !!maxContentHeight ? `max-h-[${maxContentHeight}px]` : 'h-full'
          )}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
