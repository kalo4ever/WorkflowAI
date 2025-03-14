import type { Meta, StoryObj } from '@storybook/react';
import { WorkflowAIIcon } from './WorkflowAIIcon';

const meta = {
  title: 'Components/Logo/WorkflowAIIcon',
  component: WorkflowAIIcon,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof WorkflowAIIcon>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Small: Story = {
  args: {
    ratio: 0.5,
  },
};

export const Medium: Story = {
  args: {
    ratio: 1,
  },
};

export const Large: Story = {
  args: {
    ratio: 2,
  },
};
