import type { Meta, StoryObj } from '@storybook/react';
import { Check } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

/**
 * Displays a badge or a component that looks like a badge.
 */
const meta = {
  title: 'ui/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: {
    children: {
      control: 'text',
    },
  },
  args: {
    children: 'Badge',
  },
  parameters: {
    layout: 'centered',
  },
  render: (args) => (
    <div className='flex items-center gap-2'>
      <div className='flex flex-col gap-2 items-start'>
        <div>Default</div>
        <Badge {...args} />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Icon</div>
        <Badge lucideIcon={Check} {...args} />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Closable</div>
        <Badge onClose={() => {}} {...args} />
      </div>
      <div className='flex flex-col gap-2 items-start'>
        <div>Clickable</div>
        <Badge onClick={() => {}} {...args} />
      </div>
    </div>
  ),
} satisfies Meta<typeof Badge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
  },
};

export const Tertiary: Story = {
  args: {
    variant: 'tertiary',
  },
};

export const Destructive: Story = {
  args: {
    variant: 'destructive',
  },
};

export const Warning: Story = {
  args: {
    variant: 'warning',
  },
};

export const Success: Story = {
  args: {
    variant: 'success',
  },
};
