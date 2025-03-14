import type { Meta, StoryObj } from '@storybook/react';
import { DatePicker } from './DatePicker';

/**
 * Displays rich content in a portal, triggered by a button.
 */
const meta = {
  title: 'ui/DatePicker',
  component: DatePicker,
  tags: ['autodocs'],
  argTypes: {},

  render: (args) => <DatePicker {...args} />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof DatePicker>;

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

/**
 * The date picker with time picker.
 */
export const WithTimePicker: Story = {
  args: {
    date: new Date(),
    setDate: () => {},
    withTimePicker: true,
  },
};
