import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';
import { SonnerToastContent } from './SonnerToastContent';

const meta = {
  title: 'ui/SonnerToastContent',
  component: SonnerToastContent,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof SonnerToastContent>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    type: 'success',
    title: 'Event has been created',
    description: new Date().toLocaleString(),
  },
};

export const Error: Story = {
  args: {
    type: 'error',
    title: 'Event creation failed',
    description: (
      <div className='flex items-center'>
        <span>Please log in to use WorkflowAI.</span>
        <Button variant='link' className='text-red-500 px-1 py-0 h-5'>
          Log in
        </Button>
      </div>
    ),
  },
};

export const Warning: Story = {
  args: {
    type: 'warning',
    title: 'Event is about to start',
    description: 'Please be ready.',
  },
};

export const Info: Story = {
  args: {
    type: 'info',
    title: 'Event is ongoing',
    description: 'Please join the meeting.',
  },
};
