import { cx } from 'class-variance-authority';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useDebounceCallback } from 'usehooks-ts';
import { Input } from '../ui/Input';

// We add a margin to the width evaluator to prevent the input from resizing too often
const WIDTH_EVALUATOR_MARGIN = 3;
const MIN_INPUT_WIDTH = 40;
const inputFontClasses = 'px-2 text-sm font-medium text-gray-700';

type DynamicWidthInputProps = {
  value: string;
  onChange: (newValue: string) => void;
  placeholder?: string;
  className?: string;
};

export function DynamicWidthInput(props: DynamicWidthInputProps) {
  const { value, onChange, placeholder, className } = props;

  const inputRef = useRef<HTMLInputElement>(null);
  const spanRef = useRef<HTMLSpanElement>(null);
  const [inputWidth, setInputWidth] = useState(MIN_INPUT_WIDTH);

  // We use a local state coupled with a debounced onChange to prevent the input from lagging
  const [localValue, setLocalValue] = useState(value);

  const resizeInputToValue = useCallback((newValue: string) => {
    if (spanRef.current) {
      spanRef.current.textContent = newValue;
      setInputWidth(spanRef.current.offsetWidth + WIDTH_EVALUATOR_MARGIN);
    }
    setLocalValue(newValue);
  }, []);

  useEffect(() => {
    resizeInputToValue(value);
  }, [value, resizeInputToValue]);

  const debouncedOnChange = useDebounceCallback(
    useCallback((newValue: string) => onChange(newValue), [onChange]),
    500
  );

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value;
      resizeInputToValue(newValue);
      debouncedOnChange(newValue);
    },
    [debouncedOnChange, resizeInputToValue]
  );

  return (
    <div className='relative'>
      <span
        className={cx('absolute invisible min-w-[40px]', inputFontClasses)}
        ref={spanRef}
      >
        {localValue || ''}
      </span>
      <Input
        ref={inputRef}
        value={localValue}
        onChange={handleChange}
        placeholder={placeholder}
        className={cx(
          'h-8 bg-white border border-gray-200 rounded-[2px]',
          inputFontClasses,
          className
        )}
        style={{ width: inputWidth }}
      />
    </div>
  );
}
