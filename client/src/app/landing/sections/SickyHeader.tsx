import { cx } from 'class-variance-authority';

type StickyHeaderProps = {
  firstOption: string;
  secondOption: string;
  showBackground?: boolean;
  makeTransparent?: boolean;
};

export function StickyHeader(props: StickyHeaderProps) {
  const { firstOption, secondOption, showBackground, makeTransparent } = props;

  return (
    <div
      className={cx(
        'flex w-full p-3 items-center justify-center',
        !!showBackground && 'bg-[#fffafb]/80',
        !!makeTransparent && 'opacity-0'
      )}
    >
      <div className='flex flex-row gap-1 p-[6px] rounded-[2px] bg-gray-50 border border-gray-300'>
        <div className='flex flex-1/2'>
          <div className='flex px-3 py-2 border border-gray-300 bg-white rounded-[2px] shadow-sm cursor-pointer'>
            {firstOption}
          </div>
        </div>
        <div className='flex flex-1/2'>
          <div className='flex px-3 py-2 text-gray-500 cursor-default'>{secondOption}</div>
        </div>
      </div>
    </div>
  );
}
