import { ContractUpRight16Regular } from '@fluentui/react-icons';
import { Code16Regular } from '@fluentui/react-icons';
import { Play16Regular } from '@fluentui/react-icons';
import { NumberRow16Regular } from '@fluentui/react-icons';
import { useMemo } from 'react';
import { TooltipButtonGroup } from '@/components/buttons/TooltipButtonGroup';

type TaskVersionTooltipProps = {
  children: React.ReactNode;
  onClone: () => void;
  onTryInPlayground: () => void;
  onViewCode: () => void;
  onDeploy: () => void;
  showGroupActions?: boolean;
  isInDemoMode: boolean;
};

export function TaskVersionTooltip(props: TaskVersionTooltipProps) {
  const {
    children,
    onClone,
    onTryInPlayground,
    onViewCode,
    onDeploy,
    showGroupActions = true,
    isInDemoMode,
  } = props;

  const versionActions = useMemo(() => {
    if (!showGroupActions) {
      return [];
    }
    return [
      {
        icon: <NumberRow16Regular />,
        text: 'Clone',
        onClick: onClone,
        disabled: isInDemoMode,
      },
      {
        icon: <Play16Regular />,
        text: 'Try in Playground',
        onClick: onTryInPlayground,
      },
      {
        icon: <Code16Regular />,
        text: 'View Code',
        onClick: onViewCode,
      },
      {
        icon: <ContractUpRight16Regular />,
        text: 'Deploy',
        onClick: onDeploy,
        disabled: isInDemoMode,
      },
    ];
  }, [
    showGroupActions,
    onClone,
    onTryInPlayground,
    onViewCode,
    onDeploy,
    isInDemoMode,
  ]);

  return (
    <TooltipButtonGroup items={versionActions}>{children}</TooltipButtonGroup>
  );
}
