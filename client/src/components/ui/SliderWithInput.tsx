import { SliderProps } from '@radix-ui/react-slider';
import { cx } from 'class-variance-authority';
import { useCallback } from 'react';
import { Input } from './Input';
import { Slider } from './Slider';

export type SliderWithInputProps = Omit<SliderProps, 'value' | 'defaultValue' | 'onValueChange' | 'onChange'> & {
  value: number;
  onChange: (value: number) => void;
  defaultValue?: number;
  className?: string;
};

export function SliderWithInput(props: SliderWithInputProps) {
  const { className, value, defaultValue, onChange, ...rest } = props;

  const handleSliderChange = useCallback(
    (values: number[]) => {
      onChange(values[0]);
    },
    [onChange]
  );

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      let newValue = Number(e.target.value);
      if (rest.min !== undefined && newValue < rest.min) {
        newValue = rest.min;
      } else if (rest.max !== undefined && newValue > rest.max) {
        newValue = rest.max;
      }
      onChange(newValue);
    },
    [onChange, rest.max, rest.min]
  );

  return (
    <div className={cx('flex items-center gap-2', className)}>
      <Slider
        value={[value]}
        defaultValue={defaultValue !== undefined ? [defaultValue] : undefined}
        onValueChange={handleSliderChange}
        {...rest}
      />
      <Input
        type='number'
        value={value}
        defaultValue={defaultValue}
        className='w-fit rounded-[2px] h-8 text-gray-800 text-[13px] pr-1.5'
        onChange={onInputChange}
        {...rest}
      />
    </div>
  );
}
