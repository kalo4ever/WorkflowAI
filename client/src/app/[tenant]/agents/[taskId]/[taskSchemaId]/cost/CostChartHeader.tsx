import { cn } from '@/lib/utils';

type CostChartHeaderProps = {
  headerText: string;
  topText: string;
  bottomText: string;
  showTopBorder?: boolean;
};

export function CostChartHeader(props: CostChartHeaderProps) {
  const { headerText, topText, bottomText, showTopBorder = false } = props;
  return (
    <div className='flex flex-col font-lato'>
      <div
        className={cn(
          'text-md font-semibold text-gray-700 pl-4 py-2.5 border-b border-dashed border-gray-200',
          showTopBorder && 'border-t'
        )}
      >
        {headerText}
      </div>
      <div className='flex flex-col p-4'>
        <div className='text-[13px] font-medium text-gray-500'>{topText}</div>
        <div className='text-[24px] font-semibold text-gray-900'>
          {bottomText}
        </div>
      </div>
    </div>
  );
}
