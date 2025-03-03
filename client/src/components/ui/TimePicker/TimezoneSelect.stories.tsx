import type { Meta, StoryObj } from '@storybook/react';
import { TimezoneSelect } from './TimezoneSelect';

/**
 * Displays rich content in a portal, triggered by a button.
 */
const meta = {
  title: 'ui/TimezoneSelect',
  component: TimezoneSelect,
  tags: ['autodocs'],
  argTypes: {},

  render: (args) => <TimezoneSelect {...args} />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof TimezoneSelect>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The default form of the date picker.
 */
export const Default: Story = {
  args: {
    value: 'America/New_York',
    onChange: () => {},
  },
};
