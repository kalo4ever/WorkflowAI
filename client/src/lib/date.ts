import dayjs from 'dayjs';

export function formatDate(
  date: Date | string | undefined | null,
  format: string
) {
  if (!date) {
    return 'null';
  }
  const formatted = dayjs(date).format(format);
  return formatted === 'Invalid Date' ? `${date}` : formatted;
}

export function formatDatePickerDate(
  date: Date | string | undefined | null,
  withTimePicker: boolean
) {
  const format = withTimePicker ? 'YYYY-MM-DD HH:mm:ss' : 'YYYY-MM-DD';
  return formatDate(date, format);
}
