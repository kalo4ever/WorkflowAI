import type { Meta, StoryObj } from '@storybook/react';
import { AnthropicLogo } from './AnthropicLogo';

const meta = {
  title: 'Components/Logo/AnthropicLogo',
  component: AnthropicLogo,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof AnthropicLogo>;

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
