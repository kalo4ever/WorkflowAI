import type { Meta, StoryObj } from '@storybook/react';
import { TimePicker } from './TimePicker';

/**
 * Displays rich content in a portal, triggered by a button.
 */
const meta = {
  title: 'ui/TimePicker',
  component: TimePicker,
  tags: ['autodocs'],
  argTypes: {},

  render: (args) => <TimePicker {...args} />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof TimePicker>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The default form of the date picker.
 */
export const Default: Story = {
  args: {
    date: new Date(),
    setDate: () => {},
  },
};
