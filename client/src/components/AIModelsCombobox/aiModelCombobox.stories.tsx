import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { fixtureModels, someNewUnknownModel } from '@/tests/fixtures/models';
import { AIModelCombobox, AIModelComboboxProps } from './aiModelCombobox';

function Wrapper(props: AIModelComboboxProps) {
  const [value, setValue] = useState<string>('');
  return <AIModelCombobox {...props} onModelChange={setValue} value={value} />;
}

const meta = {
  title: 'Components/AIModelCombobox',
  component: AIModelCombobox,
  tags: ['autodocs'],
  argTypes: {},
  render: (args) => <Wrapper {...args} />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof AIModelCombobox>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    value: '',
    models: [...fixtureModels, someNewUnknownModel],
    noOptionsMessage: 'Choose Model',
  },
};
