import { cx } from 'class-variance-authority';
import { AIProviderIcon } from '@/components/icons/models/AIProviderIcon';
import { Badge } from '@/components/ui/Badge';

type TaskModelBadgeProps = {
  model: string | null | undefined;
  providerId?: string | null | undefined;
  className?: string;
};

export function TaskModelBadge(props: TaskModelBadgeProps) {
  const { model, providerId, className } = props;

  if (!model) {
    return null;
  }

  return (
    <Badge variant='tertiary' className={cx('truncate flex items-center gap-1.5 max-w-[300px]', className)}>
      {providerId ? <AIProviderIcon providerId={providerId} fallbackOnMysteryIcon sizeClassName='w-4 h-4' /> : null}
      {model && <div className='truncate'>{model}</div>}
    </Badge>
  );
}
