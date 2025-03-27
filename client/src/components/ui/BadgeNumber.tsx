import { cx } from 'class-variance-authority';
import React from 'react';

type BadgeNumberProps = {
  count: number | null;
  showZero?: boolean;
  color?: string;
  children: React.ReactNode;
};

export const BadgeNumber = React.forwardRef<HTMLDivElement, BadgeNumberProps>((props, ref) => {
  const { count, showZero, color = 'bg-red-500', children } = props;
  let displayBadge = true;
  if (showZero) {
    displayBadge = count !== null;
  } else {
    displayBadge = !!count && count > 0;
  }

  return (
    <div className='relative inline-block' ref={ref}>
      {children}
      {displayBadge && (
        <span
          className={cx(
            'z-10 absolute top-0 right-0 transform translate-x-1/2 -translate-y-1/2 flex items-center justify-center text-white text-xs font-bold rounded-full h-5 w-5',
            color
          )}
        >
          {typeof count === 'number' ? count : <span className='flex items-center justify-center h-full'>{count}</span>}
        </span>
      )}
    </div>
  );
});

BadgeNumber.displayName = 'BadgeNumber';
