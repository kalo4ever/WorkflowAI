import { Dismiss12Regular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { formatSemverVersion } from '@/lib/versionUtils';
import { VersionsPerEnvironment } from '@/store/versions';
import { VersionV1 } from '@/types/workflowAI';
import { VersionEnvironment } from '@/types/workflowAI';
import { EnvironmentIcon } from '../icons/EnvironmentIcon';
import { Loader } from '../ui/Loader';

type DeployCardProps = {
  environment: VersionEnvironment;
  isSelected: boolean;
  isAlreadyDeployed: boolean;
  originalBadgeText: string | undefined;
  onDeployToggle: (environment: VersionEnvironment) => void;
};

function DeployCard(props: DeployCardProps) {
  const { environment, isSelected, isAlreadyDeployed, originalBadgeText, onDeployToggle } = props;

  const onClick = useCallback(() => {
    onDeployToggle(environment);
  }, [environment, onDeployToggle]);

  return (
    <div
      className={cx(
        'w-[240px] px-4 py-3 flex flex-col items-center rounded-[2px] border border-gray-200 bg-white',
        isSelected && 'outline outline-2 outline-slate-700 border-transparent'
      )}
    >
      <div className='w-10 h-10 rounded-full bg-custom-gradient-solid flex items-center justify-center'>
        <EnvironmentIcon environment={environment} filled={true} className='w-5 h-5 text-white' />
      </div>
      <div className='flex items-center text-[13px] mt-4 text-white capitalize bg-gray-900 font-medium px-[8px] py-[3px] gap-[6px] rounded-[2px]'>
        <EnvironmentIcon environment={environment} className='w-[14px] h-[14px] text-white' />
        {environment}
      </div>

      {originalBadgeText !== undefined ? (
        <div className='text-gray-500 text-[13px] font-normal mt-[10px]'>
          Version{' '}
          <span className='text-gray-700 px-1 py-[3px] bg-white rounded-[2px] border border-gray-200'>
            {originalBadgeText}
          </span>{' '}
          is currently deployed.
        </div>
      ) : (
        <div className='text-gray-500 text-[13px] font-normal mt-2'>No version deployed yet.</div>
      )}
      <Button
        variant={isSelected ? 'newDesignGray' : 'newDesign'}
        onClick={onClick}
        className='w-full mt-[16px]'
        disabled={isAlreadyDeployed}
      >
        {isAlreadyDeployed ? (
          'Deployed'
        ) : isSelected ? (
          'Selected'
        ) : (
          <div>
            Deploy to <span className='capitalize'>{environment}</span>
          </div>
        )}
      </Button>
    </div>
  );
}

function getOriginalBadgeText(
  environment: VersionEnvironment,
  version: VersionV1 | undefined,
  originalVersionsPerEnvironment: VersionsPerEnvironment | undefined
) {
  const orginalVersion = originalVersionsPerEnvironment?.[environment]?.[0];
  if (!orginalVersion) {
    return undefined;
  }
  return formatSemverVersion(orginalVersion);
}

function isSelected(
  environment: VersionEnvironment,
  version: VersionV1 | undefined,
  versionsPerEnvironment: VersionsPerEnvironment | undefined
) {
  const versionFromEnvironment = versionsPerEnvironment?.[environment]?.[0];
  if (!versionFromEnvironment) {
    return false;
  }
  return versionFromEnvironment.id === version?.id;
}

function isAlreadyDeployed(
  environment: VersionEnvironment,
  version: VersionV1 | undefined,
  originalVersionsPerEnvironment: VersionsPerEnvironment | undefined
) {
  const orginalVersion = originalVersionsPerEnvironment?.[environment]?.[0];
  if (!orginalVersion) {
    return false;
  }
  return orginalVersion.id === version?.id;
}

type DeployCardsProps = {
  version: VersionV1 | undefined;
  versionsPerEnvironment: VersionsPerEnvironment | undefined;
  originalVersionsPerEnvironment: VersionsPerEnvironment | undefined;
  onDeployToggle: (environment: VersionEnvironment) => void;
};

function DeployCards(props: DeployCardsProps) {
  const { onDeployToggle, version, versionsPerEnvironment, originalVersionsPerEnvironment } = props;

  const environments: VersionEnvironment[] = ['dev', 'staging', 'production'];

  return (
    <div className='flex gap-4'>
      {environments.map((environment) => (
        <DeployCard
          key={environment}
          environment={environment}
          isSelected={isSelected(environment, version, versionsPerEnvironment)}
          isAlreadyDeployed={isAlreadyDeployed(environment, version, originalVersionsPerEnvironment)}
          originalBadgeText={getOriginalBadgeText(environment, version, originalVersionsPerEnvironment)}
          onDeployToggle={onDeployToggle}
        />
      ))}
    </div>
  );
}

type DeployVersionContentProps = {
  version: VersionV1 | undefined;
  isInitialized: boolean;
  versionsPerEnvironment: VersionsPerEnvironment | undefined;
  originalVersionsPerEnvironment: VersionsPerEnvironment | undefined;
  onClose: () => void;
  onDeploy: (environment: VersionEnvironment) => void;
};

export function DeployVersionContent(props: DeployVersionContentProps) {
  const { version, isInitialized, versionsPerEnvironment, originalVersionsPerEnvironment, onClose, onDeploy } = props;

  if (!isInitialized) {
    return <Loader centered />;
  }

  return (
    <div>
      <div className='flex flex-col'>
        <div className='flex flex-row gap-4 items-center p-4 border-b border-gray-200 border-dashed'>
          <Button
            onClick={onClose}
            variant='newDesign'
            icon={<Dismiss12Regular className='w-3 h-3' />}
            className='w-7 h-7 shrink-0'
            size='none'
          />
          <div className='text-gray-900 text-[16px] font-semibold'>Deploy Version {formatSemverVersion(version)}</div>
        </div>
        <div className='text-gray-900 text-[13px] font-medium px-4 py-[18px]'>
          Select the environment you’d like to deploy version{' '}
          <span className='text-gray-700 px-1 py-[3px] bg-white rounded-[2px] border border-gray-200'>
            {formatSemverVersion(version)}
          </span>{' '}
          to:
        </div>
        <div className='flex w-full px-4 pb-4'>
          <DeployCards
            versionsPerEnvironment={versionsPerEnvironment}
            originalVersionsPerEnvironment={originalVersionsPerEnvironment}
            version={version}
            onDeployToggle={onDeploy}
          />
        </div>
      </div>
    </div>
  );
}
