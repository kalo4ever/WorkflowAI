import type { Meta, StoryObj } from '@storybook/react';
import { Loader } from '@/components/ui/Loader';

// Adjust the import path as necessary

/**
 * A component that displays a loading spinner, customizable in size and optionally centered.
 */
const meta: Meta<typeof Loader> = {
  title: 'ui/Loader',
  component: Loader,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: 'select',
      options: ['small', 'medium', 'large', 'custom'],
    },
    centered: {
      control: 'boolean',
    },
    className: {
      control: 'text',
    },
  },
  args: {
    size: 'medium',
    centered: false,
    className: '',
  },
  render: (args) => (
    <div
      style={{
        height: '200px',
        display: 'flex',
      }}
    >
      <Loader {...args} />
    </div>
  ),
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof Loader>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const XXSmall: Story = {
  args: {
    size: 'xxsmall',
  },
};

export const XSmall: Story = {
  args: {
    size: 'xsmall',
  },
};

export const Small: Story = {
  args: {
    size: 'small',
  },
};

export const Medium: Story = {
  args: {
    size: 'medium',
  },
};

export const Large: Story = {
  args: {
    size: 'large',
  },
};

export const Centered: Story = {
  args: {
    centered: true,
  },
};

export const Star: Story = {
  args: {
    star: true,
    centered: true,
  },
};
