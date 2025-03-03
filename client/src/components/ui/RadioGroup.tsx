'use client';

import * as RadioGroupPrimitive from '@radix-ui/react-radio-group';
import { cx } from 'class-variance-authority';
import { Circle } from 'lucide-react';
import * as React from 'react';
import { cn } from '@/lib/utils/cn';

const RadioGroup = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root>
>(({ className, ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Root
      className={cn('grid gap-2', className)}
      {...props}
      ref={ref}
    />
  );
});
RadioGroup.displayName = RadioGroupPrimitive.Root.displayName;

const RadioGroupItem = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item> & {
    isSelected?: boolean;
  }
>(({ className, isSelected, ...props }, ref) => {
  return (
    <RadioGroupPrimitive.Item
      ref={ref}
      className={cn(
        'aspect-square h-4 w-4 rounded-full border text-border-gray-400 ring-offset-background focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        className,
        isSelected
          ? 'border-indigo-500 text-indigo-500'
          : 'border-gray-400 text-gray-400'
      )}
      {...props}
    >
      <RadioGroupPrimitive.Indicator className='flex items-center justify-center text-indigo-500'>
        <Circle className='h-2.5 w-2.5 fill-indigo-500 text-current' />
      </RadioGroupPrimitive.Indicator>
    </RadioGroupPrimitive.Item>
  );
});
RadioGroupItem.displayName = RadioGroupPrimitive.Item.displayName;

type SimpleRadioIndicatorProps = {
  isSelected: boolean;
  onClick: () => void;
};

function SimpleRadioIndicator(props: SimpleRadioIndicatorProps) {
  const { isSelected, onClick } = props;
  return (
    <button
      onClick={onClick}
      className={cx(
        'rounded-full h-4 w-4 border flex items-center justify-center',
        isSelected ? 'border-indigo-500' : 'border-gray-400'
      )}
    >
      <Circle
        className={cx(
          'h-2.5 w-2.5 fill-current',
          isSelected ? 'text-indigo-500' : 'text-transparent'
        )}
      />
    </button>
  );
}

export { RadioGroup, RadioGroupItem, SimpleRadioIndicator };
