import { cx } from 'class-variance-authority';
import {
  AlertCircle,
  Check,
  Info,
  LucideIcon,
  MinusCircle,
} from 'lucide-react';
import { ReactNode } from 'react';

type SonnerToastType = 'success' | 'error' | 'warning' | 'info';

const SONNER_TOAST_TYPE_TO_METADATA: {
  [key in SonnerToastType]: {
    icon: LucideIcon;
    textColor: string;
    bgColor: string;
  };
} = {
  success: {
    icon: Check,
    textColor: 'text-green-600',
    bgColor: 'bg-white',
  },
  error: {
    icon: MinusCircle,
    textColor: 'text-red-600',
    bgColor: 'bg-white',
  },
  warning: {
    icon: AlertCircle,
    textColor: 'text-yellow-600',
    bgColor: 'bg-white',
  },
  info: {
    icon: Info,
    textColor: 'text-blue-500',
    bgColor: 'bg-blue-100',
  },
};

type SonnerToastContentProps = {
  type: SonnerToastType;
  title?: string | ReactNode;
  description?: string | ReactNode;
};

export function SonnerToastContent(props: SonnerToastContentProps) {
  const { type = 'info', title, description } = props;

  const {
    icon: Icon,
    textColor,
    bgColor,
  } = SONNER_TOAST_TYPE_TO_METADATA[type];

  return (
    <div className='flex items-center gap-3 pointer-events-auto'>
      <div
        className={cx(
          'h-[22px] w-[22px] flex rounded-full items-center justify-center',
          bgColor,
          textColor
        )}
      >
        {<Icon size={16} />}
      </div>
      <div className='flex flex-col text-sm'>
        {title && <div className='font-semibold'>{title}</div>}
        {description && <div>{description}</div>}
      </div>
    </div>
  );
}
