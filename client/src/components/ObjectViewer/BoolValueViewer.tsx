import { useCallback } from 'react';
import { BooleanRadioButton } from '../ui/BooleanRadioButton';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps } from './utils';

export function BoolValueViewer(props: ValueViewerProps<boolean | null>) {
  const { value, className, editable, keyPath, onEdit } = props;

  const onChange = useCallback(
    (newValue: boolean) => {
      if (!editable) {
        return;
      }
      onEdit?.(keyPath, newValue);
    },
    [editable, keyPath, onEdit]
  );

  if (!editable) {
    return <ReadonlyValue {...props} value={value} />;
  }

  return (
    <BooleanRadioButton
      value={!!value}
      onChange={onChange}
      className={className}
    />
  );
}
