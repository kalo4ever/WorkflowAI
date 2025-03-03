import type { Meta, StoryObj } from '@storybook/react';
import { CardRounded } from './CardRounded';

const meta = {
  title: 'ui/CardRounded',
  component: CardRounded,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof CardRounded>;

export default meta;

type Story = StoryObj<typeof meta>;

const children = (
  <>
    <div className='flex items-center px-4 py-3'>
      <div className='flex-1'>iteration</div>
      <div className='flex-1 text-slate-800'>1</div>
    </div>
    <div className='flex items-center px-4 py-3'>
      <div className='flex-1'>model</div>
      <div className='flex-1 text-slate-800'>gpt-3</div>
    </div>
    <div className='flex items-center px-4 py-3'>
      <div className='flex-1'>temperature</div>
      <div className='flex-1 text-slate-800'>0.7</div>
    </div>
    <div className='flex items-center px-4 py-3'>
      <div className='flex-1'>provider</div>
      <div className='flex-1 text-slate-800'>openai</div>
    </div>
  </>
);

export const Default: Story = {
  args: {
    title: 'TASK ITERATION',
    className: 'w-[400px]',
    children,
  },
};

export const WithoutTitle: Story = {
  args: {
    className: 'w-[400px]',
    children,
  },
};

export const WithoutBorder: Story = {
  args: {
    title: 'TASK ITERATION',
    className: 'w-[400px]',
    showBorder: false,
    children,
  },
};

export const DarkBackground: Story = {
  args: {
    title: 'TASK ITERATION',
    className: 'w-[400px]',
    darkBackground: true,
    children,
  },
};
