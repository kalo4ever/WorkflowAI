import type { Meta, StoryObj } from '@storybook/react';
import { MicrosoftLogo } from './MicrosoftLogo';

const meta = {
  title: 'Components/Logo/MicrosoftLogo',
  component: MicrosoftLogo,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof MicrosoftLogo>;

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
