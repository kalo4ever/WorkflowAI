import { cx } from 'class-variance-authority';
import { useMemo } from 'react';
import { StarIcon } from '@/components/icons/StarIcon';
import { cn } from '@/lib/utils';

type TaskVersionBadgeContentProps = {
  text: string | undefined;
  schemaText: string | undefined;
  isFavorite: boolean | undefined | null;
  onFavoriteToggle: (event: React.MouseEvent) => void;
  className?: string;
  showHoverState?: boolean;
  showFavorite?: boolean;
  openRightSide?: boolean;
  height?: number;
};

export function TaskVersionBadgeContent(props: TaskVersionBadgeContentProps) {
  const {
    text,
    schemaText,
    isFavorite,
    onFavoriteToggle,
    className,
    showHoverState,
    showFavorite = true,
    openRightSide = false,
    height,
  } = props;

  const heightClass = useMemo(() => {
    if (height) {
      return `h-[${height}px]`;
    }
    if (!!schemaText) {
      return 'py-[2px]';
    }
    return 'py-1';
  }, [height, schemaText]);

  return (
    <div
      className={cn(
        'flex items-center w-fit cursor-pointer',
        !!schemaText ? 'bg-gray-200 gap-1.5 pl-1.5 pr-[2px]' : 'border-gray-200 bg-white px-1.5',
        className,
        !!showHoverState && 'hover:bg-accent hover:text-accent-foreground',
        openRightSide ? 'rounded-l-[2px] border-l border-t border-b' : 'rounded-[2px] border',
        heightClass
      )}
      onClick={onFavoriteToggle}
    >
      {schemaText && <div className='font-medium text-gray-600 font-lato text-[13px]'>#{schemaText}</div>}
      <div className={cn('flex items-center gap-1', !!schemaText && 'px-1 h-full bg-white rounded-[1px]')}>
        {isFavorite !== undefined && showFavorite && (
          <StarIcon
            className={cx('w-4 h-4', isFavorite ? 'text-yellow-400' : 'text-gray-400')}
            fill={isFavorite ? '#FACC15' : undefined}
          />
        )}
        {text !== undefined && <div className='text-[13px] font-medium text-gray-700 font-lato'>{text}</div>}
      </div>
    </div>
  );
}
