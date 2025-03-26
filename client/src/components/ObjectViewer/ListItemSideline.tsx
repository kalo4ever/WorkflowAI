import { cx } from 'class-variance-authority';
import { Separator } from '../ui/Separator';

type ListItemSidelineProps = {
  arrayIndex: number | undefined;
  isRoot: boolean;
  isLast: boolean;
  showTypes?: boolean;
};

export function ListItemSideline(props: ListItemSidelineProps) {
  const { arrayIndex, isRoot, isLast, showTypes } = props;
  if (isRoot || arrayIndex === undefined) {
    return null;
  }
  return (
    <div className='flex items-center'>
      <Separator orientation='vertical' className={cx('self-start', isLast ? 'h-[50%]' : 'h-full')} />
      <Separator className='w-3' />
      <div
        className={cx('pl-4 text-gray-500 font-medium text-sm min-w-[25px]', {
          'pb-2': showTypes,
        })}
      >
        {!!showTypes ? '...' : arrayIndex + 1}
      </div>
    </div>
  );
}
