import type { Meta, StoryObj } from '@storybook/react';
import { Sailboat } from 'lucide-react';
import { AlertDialog } from '@/components/ui/AlertDialog';

const meta = {
  title: 'ui/AlertDialog',
  component: AlertDialog,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    open: true,
    title: 'Title',
    text: 'Text',
    cancelText: 'Cancel',
    confrimationText: 'Confirm',
    onCancel: () => {},
    onConfirm: () => {},
  },
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof AlertDialog>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    cancelText: 'Cancel',
    confrimationText: 'Confirmation',
  },
};

export const WithIcon: Story = {
  args: {
    icon: Sailboat,
    cancelText: 'Cancel',
    confrimationText: 'Confirmation',
  },
};

export const WithSubTitle: Story = {
  args: {
    subTitle: 'Sub Title',
    cancelText: 'Cancel',
    confrimationText: 'Confirmation',
  },
};

export const Destructive: Story = {
  args: {
    cancelText: 'Cancel',
    confrimationText: 'Confirmation',
    destructive: true,
  },
};
