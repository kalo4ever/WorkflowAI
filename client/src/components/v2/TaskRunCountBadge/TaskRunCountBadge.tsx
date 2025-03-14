import { ListBarTree20Regular } from '@fluentui/react-icons';
import { useCallback } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '@/components/ui/Tooltip';

type TaskRunCountBadgeProps = {
  runsCount: number | undefined;
  onClick?: (() => void) | undefined;
};

export function TaskRunCountBadge(props: TaskRunCountBadgeProps) {
  const { runsCount = 0, onClick } = props;

  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      event.stopPropagation();
      onClick?.();
    },
    [onClick]
  );

  return (
    <Badge variant='tertiary' onClick={!!onClick ? handleClick : undefined}>
      <div className='flex gap-1 items-center whitespace-nowrap'>
        <ListBarTree20Regular />
        <div>{runsCount}</div>
        <div>{runsCount === 1 ? 'Run' : 'Runs'}</div>
      </div>
    </Badge>
  );
}

export function TaskRunCountButton(props: TaskRunCountBadgeProps) {
  const { runsCount = 0, onClick } = props;

  const content = (
    <div className='flex gap-1 items-center px-1 text-xsm text-gray-500 whitespace-nowrap'>
      <ListBarTree20Regular />
      <div>{runsCount}</div>
    </div>
  );

  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.stopPropagation();
      onClick?.();
    },
    [onClick]
  );

  if (!onClick) {
    return content;
  }

  return (
    <SimpleTooltip content='View Runs' tooltipDelay={100}>
      <Button
        variant='ghost'
        onClick={handleClick}
        className='p-0 h-6 hover:bg-gray-200 hover:text-gray-900'
      >
        {content}
      </Button>
    </SimpleTooltip>
  );
}
