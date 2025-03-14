import { cx } from 'class-variance-authority';

type HeaderEntryProps = {
  title: string;
  className?: string;
};

function HeaderEntry(props: HeaderEntryProps) {
  const { title, className } = props;
  return (
    <div
      className={cx(
        'flex flex-row gap-0.5 text-gray-900 font-lato text-[13px] font-medium py-3 items-center overflow-hidden text-ellipsis whitespace-nowrap',
        className
      )}
    >
      {title}
    </div>
  );
}

export function TaskRunTableHeader() {
  return (
    <div className='flex flex-col w-full h-fit border-l border-r border-t border-gray-200 rounded-[2px] bg-gradient-to-b from-white/60 to-white/50'>
      <div className='flex w-full flex-none px-2'>
        <div className='flex flex-row w-full border-b border-gray-200/60'>
          <div className='flex-1'>
            <HeaderEntry title='Input' className='pl-2' />
          </div>
          <div className='flex-1'>
            <HeaderEntry title='Output' />
          </div>
          <div className='w-[60px]'>
            <HeaderEntry title='Schema' />
          </div>
          <div className='w-[140px]'>
            <HeaderEntry title='Version' />
          </div>
          <div className='w-[64px]'>
            <HeaderEntry title='Time' />
          </div>
          <div className='w-[60px]'>
            <HeaderEntry title='Review' />
          </div>
        </div>
      </div>
    </div>
  );
}
