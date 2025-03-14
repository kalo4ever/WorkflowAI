import { Meta, StoryObj } from '@storybook/react';
import { BadgeNumber } from '@/components/ui/BadgeNumber';
import { Avatar, AvatarFallback, AvatarImage } from './Avatar/Avatar';

const meta: Meta<typeof BadgeNumber> = {
  title: 'ui/BadgeNumber',
  component: BadgeNumber,
  tags: ['autodocs'],
  argTypes: {},
  render: (args) => (
    <BadgeNumber {...args}>
      <Avatar>
        <AvatarImage src='https://github.com/shadcn.png' />
        <AvatarFallback>CN</AvatarFallback>
      </Avatar>
    </BadgeNumber>
  ),
};
export default meta;

type Story = StoryObj<typeof BadgeNumber>;

export const Base: Story = {
  args: {
    count: 3,
  },
};

export const WithZeroCount: Story = {
  args: {
    count: 0,
  },
};

export const WithNullCount: Story = {
  args: {
    count: null,
  },
};

export const WithZeroCountAndShowZero: Story = {
  args: {
    count: 0,
    showZero: true,
  },
};

export const WithNullCountAndShowZero: Story = {
  args: {
    count: null,
    showZero: true,
  },
};

export const WithCustomColor: Story = {
  args: {
    count: 3,
    color: 'bg-blue-500',
  },
};
