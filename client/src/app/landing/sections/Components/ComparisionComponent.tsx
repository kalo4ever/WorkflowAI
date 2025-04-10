import Image from 'next/image';
import { useMemo } from 'react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

type FeatureCardProps = {
  value: number | undefined;
};

function FeatureCardOne(props: FeatureCardProps) {
  const { value } = props;
  const message = useMemo(() => {
    if (!value) return 'Loading...';
    const downtimeMinutes = Math.round((100 - value) * 438.336); // 43,833.6 minutes per month / 100 = 438.336 minutes per 1% downtime
    return `OpenAI's uptime is ${value}%, which means ~${downtimeMinutes} minutes of downtime per month. That's ${downtimeMinutes} minutes your AI features could be failing.`;
  }, [value]);
  return (
    <div className='flex flex-col border border-gray-200 rounded-[2px] bg-custom-gradient-1'>
      <div className='flex flex-col sm:p-6 p-4'>
        <div className='w-full aspect-[458/232] mb-6 relative'>
          <Image
            src='https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingIllustration40.jpg'
            alt='Image'
            width={458}
            height={232}
            className='w-full h-full object-cover'
          />
          {value && (
            <div className='absolute top-[-11%] left-[37%] w-[100%] h-[100%] items-center justify-center flex'>
              <div className='flex items-center justify-center text-red-600 bg-white border border-red-500 rounded-full px-2 py-[1px] text-[11px] font-semibold'>
                {value}%
              </div>
            </div>
          )}
        </div>
        <div className='sm:text-[18px] text-[16px] font-semibold text-gray-900 sm:pb-4 pb-1'>
          <span className='text-gray-500'>OpenAI</span> without WorkflowAI
        </div>
        <div className='sm:text-[16px] text-[13px] font-normal text-gray-500'>{message}</div>
        <div className='flex justify-start mt-6'>
          <Button variant='newDesignGray' openInNewTab={true} toRoute='https://status.openai.com/'>
            View OpenAI uptime
          </Button>
        </div>
      </div>
    </div>
  );
}

function FeatureCardTwo(props: FeatureCardProps) {
  const { value } = props;

  const message = useMemo(() => {
    if (!value) return 'Loading...';
    const downtimeMinutes = Math.round((100 - value) * 438.336); // 43,833.6 minutes per month / 100 = 438.336 minutes per 1% downtime
    return `OpenAI's uptime is ${value}%, which means ~${downtimeMinutes} minutes of downtime per month. That's ${downtimeMinutes} minutes your AI features could be failing.`;
  }, [value]);

  return (
    <div className='flex flex-col border border-gray-200 rounded-[2px] bg-custom-gradient-1'>
      <div className='flex flex-col sm:p-6 p-4'>
        <div className='w-full aspect-[458/232] mb-6 relative'>
          <Image
            src='https://workflowai.blob.core.windows.net/workflowai-public/landing/LandingIllustration41.jpg'
            alt='Image'
            width={458}
            height={232}
            className='w-full h-full object-cover'
          />
          {value && (
            <div className='absolute top-[-11%] left-[3%] w-[100%] h-[100%] items-center justify-center flex'>
              <div className='flex items-center justify-center text-green-600 bg-white border border-green-500 rounded-full px-2 py-[1px] text-[11px] font-semibold'>
                {value}%
              </div>
            </div>
          )}
        </div>
        <div className='sm:text-[18px] text-[16px] font-semibold text-gray-900 sm:pb-4 pb-1'>
          <span className='text-gray-500'>OpenAI</span> without WorkflowAI
        </div>
        <div className='sm:text-[16px] text-[13px] font-normal text-gray-500'>{message}</div>
        <div className='flex flex-wrap gap-4 justify-start mt-6 sm:w-full w-fit'>
          <Button variant='newDesignGray' openInNewTab={true} toRoute='https://status.workflowai.com/'>
            View WorkflowAI uptime
          </Button>
          <Button
            variant='newDesignGray'
            openInNewTab={true}
            toRoute='https://docs.workflowai.com/workflowai-cloud/reliability'
          >
            See how WorkflowAI failover system works
          </Button>
        </div>
      </div>
    </div>
  );
}

type Props = {
  className?: string;
  workflowUptime: number | undefined;
  openaiUptime: number | undefined;
};

export function ComparisionComponent(props: Props) {
  const { className, workflowUptime, openaiUptime } = props;

  return (
    <div className={cn('flex items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className='grid w-full grid-cols-1 sm:grid-cols-2 gap-6'>
        <FeatureCardOne value={openaiUptime} />
        <FeatureCardTwo value={workflowUptime} />
      </div>
    </div>
  );
}
