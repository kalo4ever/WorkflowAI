import { Copy16Regular } from '@fluentui/react-icons';
import { useMemo } from 'react';
import { TooltipButtonGroup } from '@/components/buttons/TooltipButtonGroup';

type InstructionTooltipProps = {
  children: React.ReactNode;
  onCopy: () => void;
};

export function InstructionTooltip(props: InstructionTooltipProps) {
  const { children, onCopy } = props;

  const actions = useMemo(() => {
    return [
      {
        icon: <Copy16Regular />,
        text: 'Copy',
        onClick: onCopy,
      },
    ];
  }, [onCopy]);

  return <TooltipButtonGroup items={actions}>{children}</TooltipButtonGroup>;
}
