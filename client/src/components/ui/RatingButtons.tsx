import { cx } from 'class-variance-authority';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export enum Rating {
  ThumbsUp = 'thumbs-up',
  ThumbsDown = 'thumbs-down',
}

export type RatingButtonsProps = {
  rating: Rating | undefined;
  onThumbUp?: () => void | Promise<void>;
  onThumbDown?: () => void | Promise<void>;
  disableUpdate?: boolean;
  disabled?: boolean;
  className?: string;
  buttonsClassName?: string;
};

export function RatingButtons(props: RatingButtonsProps) {
  const {
    rating,
    onThumbUp,
    onThumbDown,
    disableUpdate = false,
    disabled,
    className,
    buttonsClassName,
  } = props;

  const showButtonsSeparate = !disableUpdate && !disabled;

  return (
    <div
      className={cx(
        'flex items-center justify-center',
        className,
        showButtonsSeparate ? 'gap-1' : 'gap-0'
      )}
    >
      <Button
        variant='outline'
        icon={<ThumbsUp className='h-4 w-4' />}
        onClick={
          disabled || disableUpdate || rating === Rating.ThumbsUp
            ? undefined
            : onThumbUp
        }
        className={cx(
          rating === Rating.ThumbsUp
            ? 'bg-green-100 text-green-600 hover:bg-green-200 border-green-300'
            : undefined,
          'px-[9px]',
          !!disableUpdate && rating === Rating.ThumbsDown && 'opacity-0',
          !rating && !showButtonsSeparate && 'rounded-r-none border-r-0',
          buttonsClassName
        )}
      />

      <Button
        variant='outline'
        icon={<ThumbsDown className='h-4 w-4' />}
        onClick={
          disabled || disableUpdate || rating === Rating.ThumbsDown
            ? undefined
            : onThumbDown
        }
        className={cx(
          rating === Rating.ThumbsDown
            ? 'bg-red-50 text-red-600 hover:bg-red-100 border-red-200'
            : undefined,
          'px-[9px]',
          !!disableUpdate && rating === Rating.ThumbsUp && 'opacity-0',
          !rating && !showButtonsSeparate && 'rounded-l-none',
          buttonsClassName
        )}
      />
    </div>
  );
}
