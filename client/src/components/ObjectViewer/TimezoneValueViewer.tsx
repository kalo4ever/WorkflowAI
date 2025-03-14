import { useCallback } from 'react';
import { TimezoneSelect } from '../ui/TimePicker/TimezoneSelect';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps } from './utils';

export function TimezoneValueViewer(props: ValueViewerProps<string>) {
  const { value, editable, onEdit, keyPath } = props;

  const onChange = useCallback(
    (newValue: string) => {
      onEdit?.(keyPath, newValue);
    },
    [keyPath, onEdit]
  );

  if (!editable) {
    return <ReadonlyValue {...props} />;
  }

  return (
    <div className='mt-[-2px]'>
      <TimezoneSelect value={value} onChange={onChange} />
    </div>
  );
}
