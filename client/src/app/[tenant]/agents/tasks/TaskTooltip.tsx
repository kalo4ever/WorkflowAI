import { Cloud16Regular, Code16Regular, ListBarTree16Regular, PlayCircle16Regular } from '@fluentui/react-icons';
import { useMemo } from 'react';
import { TooltipButtonGroup } from '@/components/buttons/TooltipButtonGroup';

type TaskTooltipProps = {
  children: React.ReactNode;
  onTryInPlayground: () => void;
  onViewRuns: () => void;
  onViewCode: () => void;
  onViewDeployments: () => void;
};

export function TaskTooltip(props: TaskTooltipProps) {
  const { children, onTryInPlayground, onViewRuns, onViewCode, onViewDeployments } = props;

  const versionActions = useMemo(() => {
    return [
      {
        icon: <PlayCircle16Regular />,
        text: 'Go to Playground',
        onClick: onTryInPlayground,
      },
      {
        icon: <ListBarTree16Regular />,
        text: 'View Runs',
        onClick: onViewRuns,
      },
      {
        icon: <Code16Regular />,
        text: 'View Code',
        onClick: onViewCode,
      },
      {
        icon: <Cloud16Regular />,
        text: 'View Deployments',
        onClick: onViewDeployments,
      },
    ];
  }, [onTryInPlayground, onViewRuns, onViewCode, onViewDeployments]);

  return <TooltipButtonGroup items={versionActions}>{children}</TooltipButtonGroup>;
}
