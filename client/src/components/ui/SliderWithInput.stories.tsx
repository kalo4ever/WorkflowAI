import type { Meta, StoryObj } from '@storybook/react';
import { useCallback, useState } from 'react';
import {
  SliderWithInput,
  SliderWithInputProps,
} from '@/components/ui/SliderWithInput';

type WrapperProps = Omit<SliderWithInputProps, 'value' | 'onChange'>;

function Wrapper(props: WrapperProps) {
  const [value, setValue] = useState<number>(props.defaultValue || 1);
  const onChange = useCallback((value: number) => setValue(value), []);
  return (
    <div className='w-64'>
      <SliderWithInput {...props} value={value} onChange={onChange} />
    </div>
  );
}

const meta = {
  title: 'ui/SliderWithInput',
  component: SliderWithInput,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    value: 1,
    defaultValue: 1,
    min: 0,
    max: 4,
    step: 0.01,
  },
  render: (args: WrapperProps) => <Wrapper {...args} />,
} satisfies Meta<typeof SliderWithInput>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};
