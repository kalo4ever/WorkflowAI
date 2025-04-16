import Image from 'next/image';
import { useMemo, useState } from 'react';
import { Slider } from '@/components/ui/Slider';
import { cn } from '@/lib/utils';

type SliderProps = {
  min: number;
  max: number;
  numberOfTraces: number;
  setNumberOfTraces: (value: number) => void;
};

function SliderComponent(props: SliderProps) {
  const { min, max, numberOfTraces, setNumberOfTraces } = props;

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${num / 1000000}m`;
    }
    return num.toLocaleString();
  };

  return (
    <div className='flex flex-col w-full'>
      <div className='flex w-full justify-between items-center mb-4'>
        <div className='text-gray-700 sm:text-[16px] text-[14px] font-semibold'>Number of Traces Per Month</div>
        <div className='text-center text-gray-900 font-bold sm:text-[16px] text-[14px]'>
          {numberOfTraces.toLocaleString()}
        </div>
      </div>
      <Slider
        min={min}
        max={max}
        value={[numberOfTraces]}
        onValueChange={(value) => setNumberOfTraces(value[0])}
        step={1000}
        rangeColor='bg-gray-700'
        thumbBorderColor='border-gray-700'
      />
      <div className='flex justify-between items-center mt-3 px-2'>
        <span className='text-gray-500 text-[13px] -translate-x-1'>{formatNumber(min)}</span>
        <span className='text-gray-500 text-[13px] translate-x-1'>1m</span>
        <span className='text-gray-500 text-[13px] translate-x-1'>2m</span>
        <span className='text-gray-500 text-[13px] translate-x-1'>3m</span>
        <span className='text-gray-500 text-[13px] translate-x-1'>4m</span>
        <span className='text-gray-500 text-[13px] translate-x-1'>{formatNumber(max)}</span>
      </div>
    </div>
  );
}

type PriceCardProps = {
  price: number;
  best: boolean;
  imageURL: string;
  imageWidth: number;
  imageHeight: number;
};

function PriceCard(props: PriceCardProps) {
  const { imageURL, price, best, imageWidth, imageHeight } = props;

  return (
    <div className='flex-1 min-w-[180px] text-center'>
      <div className={cn('flex w-full rounded-[2px]', best ? 'bg-custom-gradient-solid' : 'bg-gray-200')}>
        <div
          className={cn(
            'flex flex-col w-full items-center justify-between gap-2 rounded-[1px] bg-white',
            best ? 'm-[2px] px-2 py-1' : 'm-[1px] px-[9px] py-[5px]'
          )}
        >
          <div className='flex flex-col gap-3 w-full px-1 py-2 items-start'>
            <Image src={imageURL} alt={'Image'} width={imageWidth} height={imageHeight} />
            <div
              className={cn(
                'text-center sm:text-[30px] text-[24px] font-bold',
                best ? 'text-green-600' : 'text-red-500'
              )}
            >
              ${price.toLocaleString(undefined, { maximumFractionDigits: 0 })}/yr
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

type ComparePriceComponentProps = {
  className?: string;
};

export function ComparePriceComponent(props: ComparePriceComponentProps) {
  const { className } = props;

  const [numberOfTraces, setNumberOfTraces] = useState(1000000);

  const langSmith = useMemo(() => {
    const basePrice = 39;
    const includedTraces = 10000;
    const pricePerBlock = 5.0;
    const blockSize = 1000;

    const additionalTracesPerYear = Math.max(0, numberOfTraces * 12 - includedTraces * 12);
    const additionalBlocksPerYear = Math.ceil(additionalTracesPerYear / blockSize);

    return basePrice * 12 + additionalBlocksPerYear * pricePerBlock;
  }, [numberOfTraces]);

  const langfuse = useMemo(() => {
    const basePrice = 199;
    const includedTraces = 100000;
    const pricePerBlock = 8;
    const blockSize = 100000;

    const additionalTracesPreYear = Math.max(0, numberOfTraces * 12 - includedTraces * 12);
    const additionalBlocksPerYear = Math.ceil(additionalTracesPreYear / blockSize);

    return basePrice * 12 + additionalBlocksPerYear * pricePerBlock;
  }, [numberOfTraces]);

  return (
    <div className={cn('flex flex-col items-center sm:gap-12 gap-8 sm:px-16 px-4 w-full max-w-[900px]', className)}>
      <div className='flex w-full bg-white rounded-[2px] sm:p-6 p-4 border border-gray-200 flex-col items-center justify-center gap-8'>
        <div className='text-indigo-600 font-semibold text-center sm:text-[16px] text-[14px] py-[6px] px-3 rounded-[2px] bg-indigo-50'>
          Just slide it. You’ll get it.
        </div>
        <SliderComponent min={0} max={5000000} numberOfTraces={numberOfTraces} setNumberOfTraces={setNumberOfTraces} />
        <div className='flex flex-wrap items-center justify-center gap-4 w-full'>
          <PriceCard
            price={0}
            best={true}
            imageURL={'https://workflowai.blob.core.windows.net/workflowai-public/landing/ComparisionLogo1.png'}
            imageWidth={125}
            imageHeight={20}
          />
          <PriceCard
            price={langSmith}
            best={false}
            imageURL={'https://workflowai.blob.core.windows.net/workflowai-public/landing/ComparisionLogo2.png'}
            imageWidth={128}
            imageHeight={20}
          />
          <PriceCard
            price={langfuse}
            best={false}
            imageURL={'https://workflowai.blob.core.windows.net/workflowai-public/landing/ComparisionLogo3.png'}
            imageWidth={120}
            imageHeight={20}
          />
        </div>
        <div className='text-gray-500 text-center sm:text-[16px] text-[14px] font-normal'>
          <span className='font-semibold text-gray-700'>WorkflowAI is completely free ($0)</span> for any number of
          traces, while competitors charge based on usage.
        </div>
        <div className='text-gray-500 text-center sm:text-[16px] text-[14px] font-normal max-w-[540px]'>
          How do we make money? We make money on providers volume discount.{' '}
          <a
            href='https://docs.workflowai.com/workflowai-cloud/pricing'
            target='_blank'
            rel='noopener noreferrer'
            className='underline'
          >
            Learn more about our business model.
          </a>
        </div>
      </div>
    </div>
  );
}
