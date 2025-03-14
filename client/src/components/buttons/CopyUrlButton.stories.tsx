import type { Meta, StoryObj } from '@storybook/react';
import { CopyUrlButton } from './CopyUrlButton';

const meta = {
  title: 'Components/buttons/CopyUrlButton',
  component: CopyUrlButton,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof CopyUrlButton>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};
