import { action } from '@storybook/addon-actions';
import type { Meta, StoryObj } from '@storybook/react';
import { InfoCard } from './InfoCard';

const meta = {
  title: 'ui/InfoCard',
  component: InfoCard,
  tags: ['autodocs'],
  argTypes: {},
  args: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof InfoCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    title: 'What’s going on here?',
    content:
      'Field descriptions and examples are sent to the LLM to provide more context on the individual elements of your input and output. For most tasks, changes to this information is not needed. However if you are seeing serious issues with one particular field, you can make edits to the description and examples to correct errors.',
  },
};

export const WithOnClose: Story = {
  args: {
    title: 'What’s going on here?',
    content:
      'Field descriptions and examples are sent to the LLM to provide more context on the individual elements of your input and output. For most tasks, changes to this information is not needed. However if you are seeing serious issues with one particular field, you can make edits to the description and examples to correct errors.',
    onClose: action('onClose'),
  },
};
