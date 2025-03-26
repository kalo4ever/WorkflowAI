import { cx } from 'class-variance-authority';
import { ReactNode, useCallback, useMemo } from 'react';
import CreatableSelect from 'react-select/creatable';
import { Badge } from '@/components/ui/Badge';

type EnumMultiSelectProps = {
  enumValues: string[];
  onChange: (newValue: string[]) => void;
  className?: string;
  placeholder?: string;
};

export function EnumMultiSelect(props: EnumMultiSelectProps) {
  const { enumValues, onChange, className, placeholder = 'Enter examples (optional)' } = props;

  const formattedValue = useMemo(() => enumValues.map((v) => ({ value: v, label: v })), [enumValues]);

  const handleChange = useCallback(
    (newValues: { value: string; label: string }[]) => {
      const newValue = newValues.map((v) => v.value);
      onChange(newValue);
    },
    [onChange]
  );

  const handleSingleDelete = useCallback(
    (valueToFilter: string) => {
      onChange(enumValues.filter((v) => v !== valueToFilter));
    },
    [onChange, enumValues]
  );

  return (
    <CreatableSelect
      value={formattedValue}
      options={[]}
      // @ts-expect-error - TODO - Fix the type of CreatableSelect
      onChange={handleChange}
      isMulti
      placeholder={placeholder}
      className={cx('font-lato', className)}
      styles={{
        control: (base, state) => ({
          ...base,
          borderColor: state.isFocused ? '#334155' : '#E2E8F0',
          '&:hover': {
            borderColor: state.isFocused ? '#334155' : '#E2E8F0',
          },
          boxShadow: state.isFocused ? '0 0 0 1px #334155' : 'none',
        }),
        option: (base) => ({
          ...base,
          backgroundColor: '#F1F5F9',
          fontSize: '0.875rem',
          fontWeight: 'normal',
        }),
        placeholder: (base) => ({
          ...base,
          color: '#64748B',
          fontSize: '0.875rem',
          fontWeight: 'normal',
        }),
        input: (base) => ({
          ...base,
          fontSize: '0.875rem',
          fontWeight: 'normal',
        }),
      }}
      components={{
        DropdownIndicator: null,
        ClearIndicator: undefined,
        NoOptionsMessage: () => (
          <div className='w-full text-sm text-center text-gray-500 py-2'>Start typing to add a value</div>
        ),
        MultiValue: (props: { children: ReactNode; data: { value: string; label: string } }) => {
          const { children, data } = props;
          return (
            <Badge
              variant='tertiaryWithHover'
              className='mr-1.5 bg-gray-100'
              onClose={() => handleSingleDelete(data.value)}
            >
              {children}
            </Badge>
          );
        },
      }}
    />
  );
}
