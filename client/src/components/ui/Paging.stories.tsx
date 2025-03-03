import type { Meta, StoryObj } from '@storybook/react';
import { Paging } from '@/components/ui/Paging';

const meta = {
  title: 'Components/Paging/Paging',
  component: Paging,
  tags: ['autodocs'],
  argTypes: {},
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof Paging>;

export default meta;

type Story = StoryObj<typeof meta>;

export const FirstPageIsCurrentPage: Story = {
  args: {
    numberOfPages: 100,
    currentPage: 0,
  },
};

export const MiddlePageIsCurrentPage: Story = {
  args: {
    numberOfPages: 100,
    currentPage: 50,
  },
};

export const LastPageIsCurrentPage: Story = {
  args: {
    numberOfPages: 100,
    currentPage: 99,
  },
};

export const ThereAreOnlyTwoPages: Story = {
  args: {
    numberOfPages: 2,
    currentPage: 0,
  },
};

export const ThereIsOnlyOnePageAndTheControlIsNotShowing: Story = {
  args: {
    numberOfPages: 1,
    currentPage: 0,
  },
};
