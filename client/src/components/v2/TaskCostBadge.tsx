import { cx } from 'class-variance-authority';
import { Badge } from '@/components/ui/Badge';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { formatCurrency } from '@/lib/formatters/numberFormatters';

type TaskCostBadgeProps = {
  cost: number | null | undefined;
  className?: string;
  supportTooltip?: boolean;
};

export function TaskCostBadge(props: TaskCostBadgeProps) {
  const { cost, className, supportTooltip = true } = props;

  if (cost === undefined || cost === null) {
    return null;
  }

  const content = (
    <Badge variant='tertiaryWithHover' className={cx('w-fit', className)}>
      {formatCurrency(cost * 1000)}
    </Badge>
  );

  if (supportTooltip) {
    return <SimpleTooltip content='Estimated cost per 1k runs'>{content}</SimpleTooltip>;
  }

  return content;
}

export function TaskCostView(props: TaskCostBadgeProps) {
  const { cost, className } = props;

  if (cost === undefined || cost === null) {
    return null;
  }

  return (
    <SimpleTooltip content='Estimated cost per 1k runs'>
      <div className={cx('w-fit text-gray-500 text-[13px] font-normal', className)}>{formatCurrency(cost * 1000)}</div>
    </SimpleTooltip>
  );
}
