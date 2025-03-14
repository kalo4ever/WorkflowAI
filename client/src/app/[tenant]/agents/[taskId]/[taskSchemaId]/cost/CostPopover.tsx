'use client';

import { Check, ChevronsUpDown } from 'lucide-react';
import { useCallback, useState } from 'react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/Popover';
import { cn } from '@/lib/utils';
import { TimeFrame } from './utils';

const timeFrames = [
  TimeFrame.YESTERDAY,
  TimeFrame.LAST_WEEK,
  TimeFrame.LAST_MONTH,
  TimeFrame.LAST_YEAR,
  TimeFrame.ALL_TIME,
];

type CostPopoverProps = {
  timeFrame: TimeFrame;
  onTimeFrameChange: (timeFrame: TimeFrame) => void;
};

export function CostPopover(props: CostPopoverProps) {
  const { timeFrame, onTimeFrameChange } = props;

  const [open, setOpen] = useState(false);

  const onTimeFrameSelected = useCallback(
    (timeFrame: TimeFrame) => {
      setOpen(false);
      onTimeFrameChange(timeFrame);
    },
    [onTimeFrameChange]
  );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className='flex flex-row items-center gap-2 overflow-hidden min-w-[220px] min-h-9 w-fit border border-gray-300 rounded-[2px] justify-between px-3 shadow-sm cursor-pointer hover:bg-gray-100'>
          <div className='text-sm font-normal text-gray-800'>{timeFrame}</div>
          <ChevronsUpDown className='h-4 w-4 shrink-0 text-gray-500' />
        </div>
      </PopoverTrigger>
      <PopoverContent className='w-[auto] p-1 rounded-sm border-gray-300 font-lato min-w-[220px]'>
        {timeFrames.map((element) => (
          <div
            key={element}
            className='flex w-full cursor-pointer p-2 flex-row gap-2 items-center hover:bg-gray-100 rounded-sm'
            onClick={() => onTimeFrameSelected(element)}
          >
            <Check
              size={16}
              className={cn(
                'text-indigo-600 shrink-0',
                element === timeFrame ? 'opacity-100' : 'opacity-0'
              )}
            />
            <div className='overflow-hidden text-ellipsis whitespace-nowrap max-w-full text-gray-700 text-[13px] truncate shrink-1'>
              {element}
            </div>
          </div>
        ))}
      </PopoverContent>
    </Popover>
  );
}
