import { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { BooleanRadioButton } from './BooleanRadioButton';

function Wrapper() {
  const [value, setValue] = useState<boolean>(false);
  return <BooleanRadioButton value={value} onChange={setValue} />;
}

const meta: Meta<typeof BooleanRadioButton> = {
  title: 'ui/BooleanRadioButton',
  component: BooleanRadioButton,
  tags: ['autodocs'],
  argTypes: {},
  render: Wrapper,
};
export default meta;

type Story = StoryObj<typeof BooleanRadioButton>;

export const Default: Story = {};
