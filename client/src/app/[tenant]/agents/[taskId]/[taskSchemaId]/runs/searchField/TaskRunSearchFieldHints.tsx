import { Checkmark12Regular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

type TaskRunSearchFieldHintsProps = {
  currentValue?: string;
  options: string[] | undefined;
  isVisible: boolean;
  onSelect: (option: string) => void;
  onClose?: () => void;
  labelClassName?: string;
};

export function TaskRunSearchFieldHints(props: TaskRunSearchFieldHintsProps) {
  const { options, onSelect, isVisible, onClose, currentValue, labelClassName } = props;

  const containerRef = useRef<HTMLDivElement>(null);

  const [highlightedOptionIndex, setHighlightedOptionIndex] = useState<number | undefined>(undefined);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node) && isVisible) {
        onClose?.();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, onClose]);

  useEffect(() => {
    setHighlightedOptionIndex(undefined);
  }, [options]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isVisible) return;
      if (!options) return;

      if (event.key === 'ArrowDown') {
        setHighlightedOptionIndex((prev) => {
          if (prev === undefined || prev === options.length - 1) {
            return 0;
          }
          return prev + 1;
        });
      }
      if (event.key === 'ArrowUp') {
        setHighlightedOptionIndex((prev) => {
          if (prev === undefined || prev === 0) {
            return options.length - 1;
          }
          return prev - 1;
        });
      }
      if (event.key === 'Enter' && highlightedOptionIndex !== undefined) {
        onSelect(options[highlightedOptionIndex]);
        onClose?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [highlightedOptionIndex, onSelect, options, onClose, isVisible]);

  const onSelectAndClose = useCallback(
    (option: string) => {
      onSelect(option);
      onClose?.();
    },
    [onSelect, onClose]
  );

  const isCurrentValueExistingInOptions = useMemo(() => {
    if (!currentValue || !options) return false;
    return options.includes(currentValue);
  }, [options, currentValue]);

  return (
    <div className={cx('relative -ml-3', (!isVisible || !options || options.length === 0) && 'hidden')}>
      <div
        ref={containerRef}
        className='absolute left-0 right-0 mt-2 bg-white border border-gray-200 rounded-[2px] shadow-md z-10 flex w-fit min-w-[180px]'
      >
        <div className='p-1 flex flex-col text-[13px] font-normal w-full max-h-[450px] overflow-y-auto'>
          {!!options &&
            options.map((option, index) => (
              <div
                key={option}
                onClick={() => onSelectAndClose(option)}
                className={cx(
                  'cursor-pointer px-2 py-1.5 hover:bg-gray-100 w-full rounded-[2px] flex flex-row gap-0.5 items-center',
                  index === highlightedOptionIndex ? 'bg-slate-100' : 'bg-white'
                )}
              >
                {!!currentValue && isCurrentValueExistingInOptions && (
                  <Checkmark12Regular
                    className={cx(
                      'w-[14px] h-[14px] flex-shrink-0 text-gray-900',
                      option === currentValue ? 'opacity-100' : 'opacity-0'
                    )}
                  />
                )}
                <div className={labelClassName}>{option}</div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
