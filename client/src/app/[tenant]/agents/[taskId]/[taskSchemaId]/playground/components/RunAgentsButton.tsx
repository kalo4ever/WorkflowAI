import {
  Play16Filled,
  Save16Filled,
  Stop16Filled,
} from '@fluentui/react-icons';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '@/components/ui/Tooltip';

type Props = {
  showSaveAllVersions: boolean;
  singleTaskLoading: boolean;
  inputLoading: boolean;
  areInstructionsLoading: boolean;
  onSaveAllVersions: () => void;
  onTryPromptClick: () => void;
  onStopAllRuns: () => void;
};

export function RunAgentsButton(props: Props) {
  const {
    showSaveAllVersions,
    singleTaskLoading,
    inputLoading,
    areInstructionsLoading,
    onSaveAllVersions,
    onTryPromptClick,
    onStopAllRuns,
  } = props;

  const [isHovering, setIsHovering] = useState(false);

  const isSaveButtonDisabled = inputLoading || areInstructionsLoading;

  if (showSaveAllVersions) {
    return (
      <SimpleTooltip content={'Save all as new versions'}>
        <Button
          variant='newDesignIndigo'
          icon={<Save16Filled />}
          loading={singleTaskLoading}
          disabled={isSaveButtonDisabled}
          onClick={onSaveAllVersions}
          className='min-h-8'
        >
          Save All Versions
        </Button>
      </SimpleTooltip>
    );
  }

  const isNormalButtonDisabled = inputLoading || areInstructionsLoading;

  const normalButtonContent = (
    <SimpleTooltip
      content={isNormalButtonDisabled ? undefined : '⌘ + Enter to run'}
    >
      <Button
        variant='newDesignIndigo'
        icon={<Play16Filled />}
        loading={singleTaskLoading}
        disabled={isNormalButtonDisabled}
        onClick={onTryPromptClick}
        className='min-h-8'
      >
        Run
      </Button>
    </SimpleTooltip>
  );

  const stopButtonContent = (
    <Button
      variant='newDesignIndigo'
      icon={<Stop16Filled />}
      onClick={onStopAllRuns}
      className='min-h-8'
    >
      Stop All Runs
    </Button>
  );

  return (
    <div
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {isHovering && singleTaskLoading
        ? stopButtonContent
        : normalButtonContent}
    </div>
  );
}
