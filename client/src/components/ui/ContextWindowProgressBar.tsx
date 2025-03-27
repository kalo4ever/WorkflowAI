import { SimpleTooltip } from '@/components/ui/Tooltip';
import { ContextWindowInformation } from '@/lib/taskRunUtils';

type ContextWindowProgressBarProps = {
  contextWindowInformation: ContextWindowInformation;
};

export function ContextWindowProgressBar(props: ContextWindowProgressBarProps) {
  const { contextWindowInformation } = props;

  return (
    <SimpleTooltip
      content={
        <div className='flex flex-col gap-0.5 items-center text-sx font-lato px-1 py-0.5'>
          <div className='font-semibold'>{contextWindowInformation.percentage}</div>
          <div className='font-regular'>Input tokens: {contextWindowInformation.inputTokens}</div>
          <div className='font-regular'>Output tokens: {contextWindowInformation.outputTokens}</div>
        </div>
      }
    >
      <div className='flex flex-row max-w-[136px] w-full h-full items-center'>
        <div className='flex w-full h-2 bg-gray-200 rounded-[2px] overflow-clip'>
          <div className='flex h-full bg-gray-400' style={{ width: contextWindowInformation.percentage }} />
        </div>
      </div>
    </SimpleTooltip>
  );
}
