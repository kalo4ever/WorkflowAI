import { cx } from 'class-variance-authority';
import { ChangeEvent, useCallback } from 'react';
import { Input } from '../ui/Input';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps } from './utils';

type NumberValueViewerProps = ValueViewerProps<number> & {
  integer?: boolean;
};

export function NumberValueViewer(props: NumberValueViewerProps) {
  const { value, className, editable, onEdit, keyPath, integer } = props;

  const onChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const value = parseFloat(e.target.value);
      onEdit?.(keyPath, value);
    },
    [keyPath, onEdit]
  );

  if (!editable) {
    return <ReadonlyValue {...props} value={value} />;
  }

  return (
    <Input
      type='number'
      value={value}
      onChange={onChange}
      className={cx(
        className,
        'w-full mt-[-2px] rounded-[2px] border-gray-200'
      )}
      step={integer ? 1 : 0.1}
      min={integer ? 0 : undefined}
    />
  );
}
