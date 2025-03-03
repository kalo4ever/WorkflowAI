import { Loader2 } from 'lucide-react';
import { SmallSwitch } from '@/components/ui/Switch';
import { SimpleTooltip } from '@/components/ui/Tooltip';

type TaskModalPreviewHeaderProps = {
  isPreviewOn: boolean;
  setIsPreviewOn: (isPreviewOn: boolean) => void;
  forceShowingTooltip: boolean;
  isLoadingPreviews: boolean;
};

export function TaskModalPreviewHeader(props: TaskModalPreviewHeaderProps) {
  const {
    isPreviewOn,
    setIsPreviewOn,
    forceShowingTooltip,
    isLoadingPreviews,
  } = props;

  const tooltipContent = isPreviewOn ? 'Hide Preview' : 'Tap to Show Preview';

  return (
    <div className='flex flex-row gap-2 w-full items-center'>
      <SimpleTooltip
        content={tooltipContent}
        side='top'
        tooltipClassName='whitespace-pre-line text-center'
        tooltipDelay={200}
        forceShowing={forceShowingTooltip}
      >
        <div
          className='flex flex-row gap-2 pl-4 h-[48px] items-center cursor-pointer'
          onClick={() => setIsPreviewOn(!isPreviewOn)}
        >
          <div className='text-gray-700 text-base font-semibold'>Preview</div>

          <div>
            <SmallSwitch
              checked={isPreviewOn}
              onCheckedChange={() => setIsPreviewOn(!isPreviewOn)}
              className='data-[state=checked]:bg-gray-900'
            />
          </div>
        </div>
      </SimpleTooltip>

      {isLoadingPreviews && (
        <Loader2 className='w-4 h-4 animate-spin text-gray-700' />
      )}
    </div>
  );
}
