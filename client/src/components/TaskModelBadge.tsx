import { cx } from 'class-variance-authority';
import { AIProviderIcon } from './icons/models/AIProviderIcon';
import { Badge } from './ui/Badge';

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
    <Badge variant='tertiary' className={cx('max-h-6 truncate flex items-center gap-1 max-w-[300px]', className)}>
      {providerId ? <AIProviderIcon providerId={providerId} fallbackOnMysteryIcon /> : null}
      {model && <div className='truncate'>{model}</div>}
    </Badge>
  );
}
