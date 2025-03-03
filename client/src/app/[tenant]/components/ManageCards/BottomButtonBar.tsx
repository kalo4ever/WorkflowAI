import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '@/components/ui/Tooltip';

type BottomButtonBarProps = {
  tooltipText?: string;
  actionText: string;
  isActionDisabled: boolean;
  onCancel: () => void;
  onAction: (() => void) | (() => Promise<void>) | undefined;
  type?: 'submit' | 'button';
};

export function BottomButtonBar(props: BottomButtonBarProps) {
  const {
    isActionDisabled,
    onCancel,
    onAction,
    tooltipText,
    actionText,
    type,
  } = props;
  return (
    <div className='flex flex-row gap-2 items-center justify-between px-4 py-3'>
      <Button variant='newDesignGray' onClick={onCancel}>
        Cancel
      </Button>
      <SimpleTooltip content={tooltipText} side='top' tooltipDelay={100}>
        <div>
          <Button
            type={type}
            variant='newDesignIndigo'
            disabled={isActionDisabled}
            onClick={onAction}
          >
            {actionText}
          </Button>
        </div>
      </SimpleTooltip>
    </div>
  );
}
