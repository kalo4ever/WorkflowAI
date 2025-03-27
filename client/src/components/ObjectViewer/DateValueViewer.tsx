import { cx } from 'class-variance-authority';
import dayjs from 'dayjs';
import { useCallback } from 'react';
import { formatDatePickerDate } from '@/lib/date';
import { JsonStringSchema } from '@/types';
import { DatePicker } from '../ui/DatePicker';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps } from './utils';

export function DateValueViewer(
  props: ValueViewerProps<Date | string | null, JsonStringSchema> & {
    withTimePicker?: boolean;
  }
) {
  const { value, withTimePicker = false, className, onEdit, editable } = props;

  const onChange = useCallback(
    (date: string) => {
      onEdit?.(props.keyPath, date || null);
    },
    [onEdit, props.keyPath]
  );

  if (!editable) {
    return <ReadonlyValue {...props} referenceValue={undefined} value={formatDatePickerDate(value, withTimePicker)} />;
  }

  // We use dayjs to parse the Date because the Date constructor is not timezone agnostic
  const safeValue = typeof value === 'string' ? dayjs(value).toDate() : value;

  return (
    <DatePicker
      date={safeValue || undefined}
      setDate={onChange}
      className={cx(className, '-mt-0.5')}
      withTimePicker={withTimePicker}
      disabled={!editable}
    />
  );
}
