import {
  ArrowSync16Regular,
  Code16Regular,
  Key16Regular,
} from '@fluentui/react-icons';
import { action } from '@storybook/addon-actions';
import type { Meta, StoryObj } from '@storybook/react';
import { TooltipButtonGroup, TooltipButtonProps } from './TooltipButtonGroup';

const meta = {
  title: 'Components/buttons/TooltipButtonGroup',
  component: TooltipButtonGroup,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
    style: {
      minHeight: '500px',
    },
  },
} satisfies Meta<typeof TooltipButtonGroup>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    items: [
      {
        icon: <ArrowSync16Regular />,
        text: 'Update Version',
        onClick: action('Update Version'),
      },
      {
        icon: <Code16Regular />,
        text: 'View Code',
        onClick: action('View Code'),
      },
      {
        icon: <Key16Regular />,
        text: 'Update API Key',
        onClick: action('Update API Key'),
      },
    ] as TooltipButtonProps[],
    children: <div className='flex items-center px-10 border'>Hello World</div>,
  },
};
