'use client';

import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import { Calendar as CalendarIcon } from 'lucide-react';
import * as React from 'react';
import { useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { Calendar } from '@/components/ui/Calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/Popover';
import { formatDatePickerDate } from '@/lib/date';
import { cn } from '@/lib/utils';
import { TimePicker } from './TimePicker/TimePicker';

dayjs.extend(utc);
dayjs.extend(timezone);

type DatePickerProps = {
  date: Date | undefined;
  setDate: (date: string) => void;
  withTimePicker?: boolean;
  className?: string;
  disabled?: boolean;
};

export function DatePicker(props: DatePickerProps) {
  const {
    className,
    date,
    setDate,
    withTimePicker = false,
    disabled = false,
  } = props;

  const timezone = dayjs.tz.guess();

  const handleDateChange = useCallback(
    (newDate: Date | undefined) => {
      const newDateStr = formatDatePickerDate(newDate, false);
      setDate(newDateStr);
    },
    [setDate]
  );

  const handleTimeChange = useCallback(
    (newDateTime: Date | undefined) => {
      const hours = dayjs(newDateTime).hour();
      const minutes = dayjs(newDateTime).minute();
      const seconds = dayjs(newDateTime).second();
      const newDate = dayjs(date)
        .hour(hours)
        .minute(minutes)
        .second(seconds)
        .toDate();
      const newDateStr = formatDatePickerDate(newDate, withTimePicker);
      setDate(newDateStr);
    },
    [setDate, date, withTimePicker]
  );

  return (
    <div className={className}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant={'newDesign'}
            className={cn(
              'w-[280px] justify-start text-left font-normal',
              !date && 'text-muted-foreground'
            )}
            disabled={disabled}
          >
            <CalendarIcon className='mr-2 h-4 w-4' />
            {date ? (
              formatDatePickerDate(date, withTimePicker)
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-auto p-0 rounded-[2px] border-gray-300'>
          <div className='flex'>
            <Calendar
              mode='single'
              selected={date}
              defaultMonth={date}
              onSelect={handleDateChange}
              // We set initialFocus to false because of an issue when rendering the calendar in a popover
              // See https://github.com/shadcn-ui/ui/issues/910
              initialFocus={false}
            />
            {withTimePicker && (
              <div className='flex flex-col gap-2 border-l border-gray-200'>
                <div className='p-3 border-b border-gray-200'>
                  <TimePicker setDate={handleTimeChange} date={date} />
                </div>
                <div className='p-3 flex flex-col gap-1 '>
                  <span className='pl-1 text-xs font-medium font-lato'>{`Timezone: ${timezone}`}</span>
                </div>
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
