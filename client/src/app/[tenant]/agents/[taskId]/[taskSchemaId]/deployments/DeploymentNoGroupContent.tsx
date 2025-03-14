import { CodeRegular, ContractUpRight16Regular } from '@fluentui/react-icons';
import { capitalize } from 'lodash';
import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { VersionEnvironment } from '@/types/workflowAI';

type DeploymentNoGroupContentProps = {
  environment: VersionEnvironment;
  onDeploy: () => void;
  isInDemoMode: boolean;
};

export function DeploymentNoGroupContent(props: DeploymentNoGroupContentProps) {
  const { environment, onDeploy, isInDemoMode } = props;

  return (
    <div className='w-full flex flex-col items-center justify-center py-6 gap-2'>
      <div className='text-slate-500 font-medium'>
        {`You haven't deployed a version to ${environment} yet`}
      </div>
      <div className='flex items-center gap-2'>
        <Button
          icon={<ContractUpRight16Regular />}
          variant='newDesign'
          onClick={onDeploy}
          size='sm'
          disabled={isInDemoMode}
        >
          Deploy {capitalize(environment)} Version
        </Button>
        <SimpleTooltip content='Deploy a version first'>
          <div>
            <Button
              variant='newDesign'
              disabled
              size='sm'
              fluentIcon={CodeRegular}
            >
              View Code
            </Button>
          </div>
        </SimpleTooltip>
      </div>
    </div>
  );
}
