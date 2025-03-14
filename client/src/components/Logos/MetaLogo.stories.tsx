import type { Meta, StoryObj } from '@storybook/react';
import { MetaLogo } from './MetaLogo';

const meta = {
  title: 'Components/Logo/MetaLogo',
  component: MetaLogo,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof MetaLogo>;

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
