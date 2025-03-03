import { cx } from 'class-variance-authority';
import { Badge } from '@/components/ui/Badge';

type CardRoundedProps = {
  title?: string;
  middleText?: string;
  badgeText?: string;
  headerChildren?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
  showBorder?: boolean;
  darkBackground?: boolean;
};

export function CardRounded(props: CardRoundedProps) {
  const {
    title,
    middleText,
    badgeText,
    headerChildren,
    className,
    showBorder = true,
    darkBackground = false,
    children,
  } = props;
  return (
    <div
      className={cx(
        className,
        showBorder === true && 'border',
        darkBackground ? 'bg-slate-50' : 'bg-white',
        'flex flex-col text-slate-600 text-[14px] rounded-[12px] overflow-clip [&>div]:border-b [&>*:last-child]:border-b-0'
      )}
    >
      {(!!title || !!middleText || !!badgeText || !!headerChildren) && (
        <div
          className={cx(
            'flex w-full px-[16px] py-[8px] items-center bg-slate-50'
          )}
        >
          <div className='flex-1 text-slate-500 text-[14px] font-medium py-[4px]'>
            {title}
          </div>
          {!!middleText && (
            <div className='flex-1 font-medium text-slate-700 text-[14px]'>
              {middleText}
            </div>
          )}
          {!!badgeText && (
            <Badge variant='tertiaryWithHover'>{badgeText}</Badge>
          )}
          {!!headerChildren && headerChildren}
        </div>
      )}
      {children}
    </div>
  );
}
