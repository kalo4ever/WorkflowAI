import type { Meta, StoryObj } from '@storybook/react';
import { useCallback, useState } from 'react';
import { TemperatureSliderSelector } from './TemperatureSliderSelector';

function Wrapper() {
  const [value, setValue] = useState<number>(1);
  const onChange = useCallback((value: number) => setValue(value), []);
  return (
    <TemperatureSliderSelector temperature={value} setTemperature={onChange} />
  );
}

const meta = {
  title: 'Components/TemperatureSliderSelector',
  component: TemperatureSliderSelector,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    temperature: 1,
  },
  render: () => <Wrapper />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof TemperatureSliderSelector>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
