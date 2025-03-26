import { LoaderIcon } from 'lucide-react';
import React from 'react';

const sizeClasses = {
  xxsmall: 'h-4 w-4 border-2',
  xsmall: 'h-6 w-6 border-2',
  small: 'h-8 w-8 border-4',
  medium: 'h-12 w-12 border-4',
  large: 'h-16 w-16 border-4',
};

type LoaderProps = {
  size?: keyof typeof sizeClasses;
  centered?: boolean;
  className?: string;
  star?: boolean;
};

export function Loader(props: LoaderProps) {
  const { size = 'medium', centered = false, star, className = '' } = props;
  const spinnerClass = `animate-spin rounded-full border-t-transparent ${sizeClasses[size]} ${className}`;

  const containerClasses = `${centered ? 'h-full w-full flex items-center justify-center min-h-[200px] min-w-[300px]' : ''}`;

  return (
    <div className={containerClasses}>
      {star ? (
        <LoaderIcon className={`animate-spin ${sizeClasses[size]} ${className}`} />
      ) : (
        <div className={spinnerClass} />
      )}
    </div>
  );
}
