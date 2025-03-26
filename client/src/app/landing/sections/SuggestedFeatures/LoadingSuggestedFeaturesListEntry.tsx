import { PlaceholderRectangle } from './PlaceholderRectangle';

export function LoadingSuggestedFeaturesListEntry() {
  return (
    <div className='flex flex-col text-start'>
      <div className='relative w-full'>
        <div className='w-full' style={{ paddingTop: '71.49%' }}></div>
        <div className='absolute inset-0 flex items-center justify-center bg-gray-50 rounded-[4px]'>
          <div className='flex px-12 w-full'>
            <div className='flex flex-col gap-3 bg-white rounded-[2px] w-full p-4 animate-pulse'>
              <PlaceholderRectangle className='w-[20%] h-[16px] animate-pulse' />
              <PlaceholderRectangle className='w-[40%] h-[16px] animate-pulse' />
              <PlaceholderRectangle className='w-[40%] h-[16px] animate-pulse' />
              <PlaceholderRectangle className='w-[70%] h-[16px] animate-pulse' />
            </div>
          </div>
        </div>
      </div>
      <div className='flex flex-col gap-2 py-4 animate-pulse'>
        <PlaceholderRectangle className='w-[30%] h-[12px]' />
        <PlaceholderRectangle className='w-[100%] h-[12px]' />
        <PlaceholderRectangle className='w-[60%] h-[12px]' />
        <PlaceholderRectangle className='w-[20%] h-[12px] mt-2' />
      </div>
    </div>
  );
}
