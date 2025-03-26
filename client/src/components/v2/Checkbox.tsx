import { Checkmark16Filled } from '@fluentui/react-icons';
import { Loader2 } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils/cn';

type CheckboxProps = {
  className?: string;
  checked: boolean;
  onClick: () => void;
  children?: React.ReactNode;
};

export function CircleCheckbox(props: CheckboxProps) {
  const { checked, onClick, className, children } = props;

  return (
    <div className='flex flex-row items-center gap-2 cursor-pointer' onClick={onClick}>
      <div className={cn('flex items-center justify-center p-0.5', className)}>
        <div
          className={cn(
            'flex w-full h-full rounded-full items-center justify-center border p-0.5',
            checked ? 'border-indigo-600' : 'border-gray-400'
          )}
        >
          <div className={cn('rounded-full w-full h-full', checked ? 'bg-indigo-600' : 'bg-transparent')} />
        </div>
      </div>
      {children}
    </div>
  );
}

export function SquareCheckbox(props: CheckboxProps) {
  const { checked, onClick, children, className } = props;

  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    try {
      await onClick();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn('flex flex-row gap-2 cursor-pointer items-center', className)} onClick={handleClick}>
      {isLoading ? (
        <Loader2 className='h-3 w-3 animate-spin text-indigo-600' />
      ) : (
        <div
          className={cn(
            'flex w-3 h-3 rounded-[3px] items-center justify-center border',
            checked ? 'border-indigo-600 bg-indigo-600' : 'border-gray-400'
          )}
        >
          <Checkmark16Filled className='w-[9px] h-[9px] text-white' />
        </div>
      )}
      {children}
    </div>
  );
}
