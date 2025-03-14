import dayjs from 'dayjs';
import { useCallback, useMemo } from 'react';
import { TimePicker } from '../ui/TimePicker/TimePicker';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps } from './utils';

export function TimeValueViewer(props: ValueViewerProps<string>) {
  const { value, editable, onEdit, keyPath } = props;

  const onChange = useCallback(
    (newDate: Date | undefined) => {
      const newValue = newDate ? dayjs(newDate).format('HH:mm:ss') : '';
      onEdit?.(keyPath, newValue);
    },
    [keyPath, onEdit]
  );

  const date: Date | undefined = useMemo(() => {
    if (value) {
      return dayjs()
        .set('hour', parseInt(value.slice(0, 2)))
        .set('minute', parseInt(value.slice(3, 5)))
        .set('second', parseInt(value.slice(6, 8)))
        .toDate();
    }
    return undefined;
  }, [value]);

  if (!editable) {
    return <ReadonlyValue {...props} />;
  }

  return <TimePicker date={date} setDate={onChange} />;
}
