import { Link16Regular, Open16Regular } from '@fluentui/react-icons';
import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '../ui/Tooltip';

type TaskRunRightActionsProps = {
  togglePromptModal: () => void;
  disablePromptButton: boolean;
  playgroundFullRoute: string | undefined;
  copyTaskRunURL: () => void;
};

export function TaskRunRightActions(props: TaskRunRightActionsProps) {
  const { togglePromptModal, disablePromptButton, playgroundFullRoute, copyTaskRunURL } = props;
  return (
    <div className='flex items-center gap-[8px]'>
      {playgroundFullRoute && (
        <SimpleTooltip
          content={
            <div className='text-center'>
              Open the playground with the version
              <br />
              and input from this run prefilled.
            </div>
          }
        >
          <Button toRoute={playgroundFullRoute} icon={<Open16Regular />} variant='newDesign'>
            Try in Playground
          </Button>
        </SimpleTooltip>
      )}
      <Button variant='newDesign' icon={<Link16Regular />} onClick={copyTaskRunURL} className='w-9 h-9 px-0 py-0' />
      <Button variant='newDesign' onClick={togglePromptModal} disabled={disablePromptButton}>
        View Prompt
      </Button>
    </div>
  );
}
