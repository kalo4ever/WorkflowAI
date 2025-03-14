import type { Meta, StoryObj } from '@storybook/react';
import {
  WorkflowAILogoWithIcon,
  WorkflowAILogoWithIconProps,
} from './WorkflowAILogoWithIcon';

function Wrapper(props: WorkflowAILogoWithIconProps) {
  return (
    <div className='w-[400px] h-[100px] flex items-center justify-center bg-slate-300'>
      <WorkflowAILogoWithIcon {...props} />
    </div>
  );
}

const meta = {
  title: 'Components/Logo/WorkflowAILogoWithIcon',
  component: WorkflowAILogoWithIcon,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
  render: (args) => <Wrapper {...args} />,
} satisfies Meta<typeof WorkflowAILogoWithIcon>;

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

export const White: Story = {
  args: {
    ratio: 1,
    color: 'white',
  },
};
