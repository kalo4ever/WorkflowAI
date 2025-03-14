import { Meta, StoryObj } from '@storybook/react';
import { StringValueViewer } from './StringValueViewer';

const meta = {
  title: 'Components/ObjectViewer/StringValueViewer',
  component: StringValueViewer,
  parameters: {
    layout: 'centered',
  },
  args: {
    keyPath: 'email.body_without_html',
    defs: undefined,
  },
  argTypes: {},
} satisfies Meta<typeof StringValueViewer>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Short: Story = {
  args: {
    value: 'Hello',
  },
};

export const Long: Story = {
  args: {
    value:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
  },
};
