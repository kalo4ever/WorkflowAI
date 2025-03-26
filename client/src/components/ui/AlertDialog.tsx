'use client';

import { LucideIcon } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent } from '@/components/ui/Dialog';

type AlertDialogProps = {
  open: boolean;
  icon?: LucideIcon;
  title: string;
  subTitle?: string;
  text: string;
  cancelText?: string;
  confrimationText?: string;
  destructive?: boolean;
  onCancel?: () => void;
  onConfirm: () => void;
};

export function AlertDialog(props: AlertDialogProps) {
  const {
    open,
    title,
    subTitle,
    text,
    cancelText = 'Cancel',
    confrimationText = 'Confirm',
    icon: Icon,
    destructive,
    onCancel,
    onConfirm,
  } = props;

  return (
    <Dialog open={open}>
      <DialogContent className='w-[420px] p-0 items-center justify-center overflow-hidden'>
        <div className='w-[420px] flex flex-col bg-custom-gradient-1'>
          <div className='pt-[14px] pb-[16px]'>
            {Icon && (
              <div className='flex px-4 w-full items-center justify-center pt-2 pb-1'>
                <Icon size={50} className='text-gray-300' />
              </div>
            )}

            <div className='w-full flex flex-col'>
              <div className='px-4 text-gray-900 font-semibold text-[16px] border-b border-dashed pb-[14px]'>
                {title}
              </div>

              <div className='flex flex-col mt-[16px]'>
                {subTitle && <div className='px-4 text-gray-800 font-medium text-[13px] mb-[14px]'>{subTitle}</div>}
                <div className='px-4 text-gray-400 font-normal text-[13px]'>{text}</div>
              </div>
            </div>
          </div>

          <div className='flex gap-[8px] w-full justify-between px-4 py-3'>
            {!!onCancel ? (
              <Button variant='newDesignGray' onClick={onCancel}>
                <div>{cancelText}</div>
              </Button>
            ) : (
              <div className='w-0 flex-0 invisible' />
            )}
            <Button variant={destructive ? 'destructive' : 'newDesign'} onClick={onConfirm}>
              {confrimationText}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
