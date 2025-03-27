import { Combobox } from '@/components/ui/Combobox';

const TIMEZONES = Intl.supportedValuesOf('timeZone').map((tz) => ({
  label: tz,
  value: tz,
}));

type TimezoneSelectProps = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

export function TimezoneSelect(props: TimezoneSelectProps) {
  const { value, onChange, disabled } = props;

  return <Combobox value={value} onChange={onChange} options={TIMEZONES} disabled={disabled} />;
}
