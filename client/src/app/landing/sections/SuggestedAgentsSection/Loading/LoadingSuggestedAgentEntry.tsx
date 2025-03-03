import { PlaceholderRectangle } from './PlaceholderRectangle';

export function LoadingSuggestedAgentEntry() {
  return (
    <div
      className={
        'flex flex-col gap-1 rounded-[4px] text-start p-4 justify-between border border-gray-100 bg-white'
      }
    >
      <div className='flex flex-col w-full items-start justify-center animate-pulse'>
        <PlaceholderRectangle className='w-[30%] h-[12px]' />
        <div className={'flex flex-col w-full gap-1.5 pt-[4px]'}>
          <PlaceholderRectangle className='w-full h-[14px]' />
          <PlaceholderRectangle className='w-full h-[14px]' />
          <PlaceholderRectangle className='w-[90%] h-[14px]' />
        </div>
      </div>
      <PlaceholderRectangle className='px-[6px] py-1 w-[25%] h-[16px] mt-2 animate-pulse' />
    </div>
  );
}
