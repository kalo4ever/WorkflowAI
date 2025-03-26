import { type VariantProps, cva } from 'class-variance-authority';
import { LucideIcon } from 'lucide-react';
import * as React from 'react';
import { HiX } from 'react-icons/hi';
import { cn } from '@/lib/utils/cn';

const badgeVariants = cva(
  'px-1.5 py-0.5 min-h-6 inline-flex items-center gap-1 text-[13px] rounded-[2px] font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'bg-gray-700 text-gray-50',
        secondary: 'bg-gray-50 text-gray-500 border border-gray-200',
        tertiary: 'bg-white text-gray-700 border border-gray-200',
        tertiaryWithHover: 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-100',
        destructive: 'bg-red-50 text-red-700 border border-red-200',
        warning: 'bg-yellow-50 text-yellow-700 border border-yellow-200',
        success: 'bg-green-50 text-green-700 border border-green-200',
      },
      clickable: {
        true: 'cursor-pointer hover:opacity-90',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {
  onClose?: () => void;
  lucideIcon?: LucideIcon;
  icon?: React.ReactNode;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, lucideIcon: Icon, icon: externalIcon, variant, onClose, children, ...props }, ref) => {
    const icon = Icon ? <Icon className='w-4 h-4' /> : externalIcon;
    return (
      <div ref={ref} className={cn(badgeVariants({ variant, clickable: !!props.onClick }), className)} {...props}>
        {icon}
        {children}
        {onClose && (
          <button className='rounded-md w-4 h-4 flex items-center justify-center' onClick={onClose}>
            <HiX className='w-3 h-3' />
            <span className='sr-only'>Remove</span>
          </button>
        )}
      </div>
    );
  }
);
Badge.displayName = 'Badge';

export { Badge, badgeVariants };
