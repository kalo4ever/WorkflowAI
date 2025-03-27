'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import * as React from 'react';
import { DayPicker } from 'react-day-picker';
import { buttonVariants } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cn';

export type CalendarProps = React.ComponentProps<typeof DayPicker>;

// This component uses date-fns under the hood

function Calendar({ className, classNames, showOutsideDays = true, ...props }: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn('p-3 font-lato', className)}
      classNames={{
        months: 'flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0',
        month: 'space-y-4',
        caption: 'flex justify-center pt-1 relative items-center',
        caption_label: 'text-[13px] font-medium',
        nav: 'space-x-1 flex items-center',
        nav_button: cn(
          buttonVariants({ variant: 'newDesign' }),
          'h-7 w-7 p-0 opacity-50 hover:opacity-100 text-gray-900'
        ),
        nav_button_previous: 'absolute left-1',
        nav_button_next: 'absolute right-1',
        table: 'w-full border-collapse space-y-1',
        head_row: 'flex',
        head_cell: 'text-gray-500 rounded-[2px] w-9 font-normal text-[0.8rem]',
        row: 'flex w-full mt-2',
        cell: 'text-gray-900 h-9 w-9 text-center text-[13px] p-0 relative [&:has([aria-selected].day-range-end)]:rounded-r-[2px] [&:has([aria-selected].day-outside)]:bg-accent/50 [&:has([aria-selected])]:bg-accent first:[&:has([aria-selected])]:rounded-l-[2px] last:[&:has([aria-selected])]:rounded-r-[2px] focus-within:relative focus-within:z-20',
        day: cn(
          buttonVariants({ variant: 'ghost' }),
          'h-9 w-9 p-0 font-normal aria-selected:opacity-100 rounded-[2px] hover:bg-gray-100'
        ),
        day_range_end: 'day-range-end',
        day_selected:
          'bg-gray-900 rounded-[2px] text-white hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground',
        day_today: 'bg-accent text-accent-foreground',
        day_outside:
          'day-outside text-gray-400 opacity-50 aria-selected:bg-gray-100 aria-selected:text-gray-900 rounded-[2px]',
        day_disabled: 'text-muted-foreground opacity-50',
        day_range_middle: 'aria-selected:bg-accent aria-selected:text-accent-foreground',
        day_hidden: 'invisible',
        ...classNames,
      }}
      components={{
        IconLeft: () => <ChevronLeft className='h-4 w-4' />,
        IconRight: () => <ChevronRight className='h-4 w-4' />,
      }}
      {...props}
    />
  );
}
Calendar.displayName = 'Calendar';

export { Calendar };
