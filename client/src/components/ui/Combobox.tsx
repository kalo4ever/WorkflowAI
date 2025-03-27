'use client';

import { ChevronUpDownFilled } from '@fluentui/react-icons';
import { Check } from 'lucide-react';
import * as React from 'react';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/Command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover';
import { cn } from '@/lib/utils';
import { Button } from './Button';
import { ScrollArea } from './ScrollArea';

export type ComboboxOption = {
  value: string;
  label: string;
  renderLabel?: React.ReactNode;
};

type ComboboxProps = {
  disabled?: boolean;
  emptyMessage?: string;
  noOptionsMessage?: string;
  onChange: (value: string) => void;
  options: ComboboxOption[];
  placeholder?: string;
  value: string;
};

export function Combobox(props: ComboboxProps) {
  const {
    disabled,
    emptyMessage = 'No option found',
    noOptionsMessage = 'Select an option...',
    onChange,
    options,
    placeholder = 'Search...',
    value,
  } = props;
  const [open, setOpen] = React.useState(false);

  let buttonContent: string | React.ReactNode = noOptionsMessage;
  const option = options.find((framework) => framework.value === value);
  if (option) {
    buttonContent = option.renderLabel || option.label;
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild disabled={disabled}>
        <Button
          variant='newDesign'
          role='combobox'
          aria-expanded={open}
          className='w-[auto] justify-between text-[13px]'
        >
          {buttonContent}
          <ChevronUpDownFilled className='ml-2 h-4 w-4 shrink-0 text-gray-500' />
        </Button>
      </PopoverTrigger>
      <PopoverContent className='w-[auto] p-0 overflow-clip rounded-[2px] border-gray-300 font-lato'>
        <Command>
          <CommandInput placeholder={placeholder} className='text-[13px] font-normal font-lato' />
          <CommandEmpty>{emptyMessage}</CommandEmpty>
          <ScrollArea>
            <CommandList>
              <CommandGroup>
                {options.map((option) => (
                  <CommandItem
                    key={option.value}
                    value={option.value}
                    onSelect={() => {
                      const currentValue = option.value;
                      if (currentValue !== value) {
                        onChange(currentValue);
                      }
                      setOpen(false);
                    }}
                    className='flex items-center gap-2 py-1.5'
                  >
                    <Check
                      className={cn(
                        'text-indigo-600 shrink-0 h-4 w-4',
                        value === option.value ? 'opacity-100' : 'opacity-0'
                      )}
                    />
                    <div
                      title={option.label}
                      className='overflow-hidden text-ellipsis whitespace-nowrap max-w-full text-gray-700 text-[13px] truncate shrink-1'
                    >
                      {option.label}
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </ScrollArea>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
