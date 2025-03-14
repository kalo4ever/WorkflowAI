import { DialogProps } from '@radix-ui/react-dialog';
import type { Meta, StoryObj } from '@storybook/react';
import { useCallback, useState } from 'react';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTrigger,
} from '@/components/ui/Dialog';

function Wrapper(props: DialogProps) {
  const [open, setOpen] = useState(false);
  const onClose = useCallback(() => setOpen(false), [setOpen]);
  return (
    <Dialog {...props} open={open} onOpenChange={setOpen}>
      <DialogTrigger>Open</DialogTrigger>
      <DialogContent className='p-0 gap-0'>
        <DialogHeader title='Are you absolutely sure?' onClose={onClose} />
        <DialogDescription className='p-4'>
          This action cannot be undone. This will permanently delete your
          account and remove your data from our servers.
        </DialogDescription>
        <DialogFooter className='p-4 gap-4'>
          <button className='hover:underline'>Cancel</button>
          <DialogClose>
            <button className='rounded bg-primary px-4 py-2 text-primary-foreground'>
              Continue
            </button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

/**
 * A window overlaid on either the primary window or another dialog window,
 * rendering the content underneath inert.
 */
const meta = {
  title: 'ui/Dialog',
  component: Dialog,
  tags: ['autodocs'],
  argTypes: {},
  render: (args) => <Wrapper {...args} />,
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof Dialog>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The default form of the dialog.
 */
export const Default: Story = {};
