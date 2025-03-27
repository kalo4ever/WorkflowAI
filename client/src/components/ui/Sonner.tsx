'use client';

import { useTheme } from 'next-themes';
import { ReactNode } from 'react';
import { Toaster as Sonner, toast } from 'sonner';
import { SonnerToastContent } from './SonnerToastContent';

type ToasterProps = React.ComponentProps<typeof Sonner>;

export const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = 'system' } = useTheme();

  return (
    <Sonner
      theme={theme as ToasterProps['theme']}
      toastOptions={{
        classNames: {
          toast:
            'px-3 py-2.5 w-[330px] group toast shadow-sm shadow-black/30 text-semibold text-[13px] rounded-[2px] border-none',
          actionButton: 'bg-primary text-primary-foreground',
          cancelButton: 'bg-muted text-muted-foreground',
          loading: 'bg-white text-gray-500 border border-gray-300',
          success: 'bg-green-600 text-white',
          error: 'bg-red-600 text-white',
          info: 'border-blue-100 text-blue-500',
          warning: 'border-yellow-100 text-yellow-500',
        },
      }}
      {...props}
    />
  );
};

export function displaySuccessToaster(message: string | ReactNode, title?: string | ReactNode) {
  toast.success(<SonnerToastContent type='success' title={title} description={message} />);
}

export function displayErrorToaster(message: string | ReactNode, title?: string | ReactNode) {
  toast.error(<SonnerToastContent type='error' title={title} description={message} />);
}
