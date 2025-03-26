import { cx } from 'class-variance-authority';
import { useCallback } from 'react';

type BooleanRadioButtonOptionProps = {
  value: boolean;
  option: boolean;
  onChange: (value: boolean) => void;
};

function BooleanRadioButtonOption(props: BooleanRadioButtonOptionProps) {
  const { value, option, onChange } = props;

  const selected = value === option;

  const onClick = useCallback(() => {
    onChange(option);
  }, [onChange, option]);

  return (
    <div
      className={cx('w-[50px] h-7 flex items-center justify-center text-sm rounded-[2px] cursor-pointer', {
        'text-gray-500 font-normal': !selected,
        'text-gray-700 font-medium bg-white outline outline-1 outline-gray-200': selected,
      })}
      onClick={onClick}
    >
      {option ? 'True' : 'False'}
    </div>
  );
}

type BooleanRadioButtonProps = {
  value: boolean;
  onChange: (value: boolean) => void;
  className?: string;
};

export function BooleanRadioButton(props: BooleanRadioButtonProps) {
  const { value, onChange, className } = props;

  return (
    <div className={cx('flex rounded-[2px] bg-gray-50 w-fit outline outline-1 outline-gray-200', className)}>
      <BooleanRadioButtonOption value={value} option={true} onChange={onChange} />
      <BooleanRadioButtonOption value={value} option={false} onChange={onChange} />
    </div>
  );
}
