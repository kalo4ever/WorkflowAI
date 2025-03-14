import { Temperature16Regular } from '@fluentui/react-icons';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';

function getTemperature(temperature: number | undefined | null) {
  switch (temperature) {
    case 0:
      return 'Precise';
    case 0.5:
      return 'Balanced';
    case 1:
      return 'Creative';
    default:
      return Number(temperature ?? 0).toFixed(1);
  }
}

type TaskTemperatureBadgeProps = {
  temperature: number | undefined | null;
  className?: string;
};

export function TaskTemperatureBadge(props: TaskTemperatureBadgeProps) {
  const { temperature, className } = props;

  return (
    <Badge variant='tertiary' className={cn('h-[26px]', className)}>
      <Temperature16Regular />
      {getTemperature(temperature)}
    </Badge>
  );
}

export function TaskTemperatureView(props: TaskTemperatureBadgeProps) {
  const { temperature, className } = props;

  return (
    <div
      className={cn(
        'flex w-fit text-gray-500 text-[13px] font-normal items-center gap-1',
        className
      )}
    >
      <Temperature16Regular />
      {getTemperature(temperature)}
    </div>
  );
}
