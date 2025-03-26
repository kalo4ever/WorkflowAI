import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { EnumMultiSelect } from './EnumMultiSelect';

type WrapperProps = {
  enumValues: string[];
};

function Wrapper({ enumValues }: WrapperProps) {
  const [selectedValues, setSelectedValues] = useState<string[]>(enumValues);
  return <EnumMultiSelect enumValues={selectedValues} onChange={setSelectedValues} />;
}

const meta = {
  title: 'ui/EnumMultiSelect',
  component: EnumMultiSelect,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
  render: Wrapper,
} satisfies Meta<typeof EnumMultiSelect>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    enumValues: ['value1', 'value2', 'value3'],
  },
};
