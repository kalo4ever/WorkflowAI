import { Checkmark12Filled } from '@fluentui/react-icons';
import { cn } from '@/lib/utils';

type HeaderEntryProps = {
  text: string;
  href?: string;
  onClick?: () => void;
};

function HeaderEntry(props: HeaderEntryProps) {
  const { text, href, onClick } = props;

  if (!href && !onClick) {
    return (
      <div className='flex flex-row gap-[6px] items-center'>
        <Checkmark12Filled className='text-gray-700' />
        <div className='text-[16px] text-gray-500 font-normal'>{text}</div>
      </div>
    );
  }

  return (
    <div className='flex flex-row gap-[6px] items-center'>
      <Checkmark12Filled className='text-gray-700' />
      <a
        href={href}
        className='text-[16px] text-gray-500 font-normal underline cursor-pointer'
        target='_blank'
        onClick={onClick}
      >
        {text}
      </a>
    </div>
  );
}

type HeaderSectionProps = {
  scrollToPricing: () => void;
  className?: string;
};

export function HeaderSection(props: HeaderSectionProps) {
  const { className, scrollToPricing } = props;

  return (
    <div className={cn('flex flex-col items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className='sm:text-[60px] text-[48px] text-gray-900 font-semibold text-center leading-[1.1]'>
        Build AI features your users will love.
      </div>
      <div className='sm:text-[24px] text-[18px] text-gray-500 font-normal text-center leading-[1.5] max-w-[860px] mt-4'>
        WorkflowAI is an open-source platform where product and engineering teams collaborate to build and iterate on AI
        features.
      </div>
      <div className='flex sm:flex-wrap sm:flex-row flex-col sm:gap-4 gap-1 mt-4 items-center justify-center'>
        <HeaderEntry text='Open-Source (deploy anywhere)' href='https://github.com/workflowai/workflowai' />
        <HeaderEntry text='Compatible with any backend' />
        <HeaderEntry text='No markup from AI providers' onClick={scrollToPricing} />
      </div>
    </div>
  );
}
