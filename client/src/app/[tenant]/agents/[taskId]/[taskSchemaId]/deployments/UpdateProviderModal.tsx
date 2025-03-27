import { FluentIcon, KeyFilled, KeyMultipleFilled } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback, useMemo } from 'react';
import { AIProviderMetadata, AI_PROVIDERS_METADATA } from '@/components/AIModelsCombobox/utils';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader } from '@/components/ui/Dialog';
import { PROVIDER_KEYS_MODAL_OPEN, useQueryParamModal } from '@/lib/globalModal';
import { Provider, VersionV1 } from '@/types/workflowAI';
import { GradientBackground } from './GradiantBackground';

type ProviderSelectionCardProps = {
  icon: FluentIcon;
  title: string;
  selected: boolean;
  onClick: () => Promise<void>;
  disabled?: boolean;
};

function ProviderSelectionCard(props: ProviderSelectionCardProps) {
  const { icon: Icon, title, selected, onClick, disabled = false } = props;
  return (
    <div
      className={cx(
        'w-[320px] flex flex-col items-center gap-3 px-4 py-3 border',
        selected && 'border-gray-900 border-2'
      )}
    >
      <div className='relative flex items-center justify-center w-10 h-10 rounded-full'>
        <GradientBackground size={40} className='absolute top-0 left-0' />
        <Icon className='w-5 h-5 text-white z-10' />
      </div>
      <div className='text-gray-500 text-xs font-medium text-center whitespace-nowrap'>{title}</div>
      <Button variant='newDesign' onClick={onClick} className='w-full' disabled={disabled || selected}>
        {selected ? 'Selected' : 'Tap to Switch'}
      </Button>
    </div>
  );
}

type UpdateProviderModalContentProps = {
  providerMetadata: AIProviderMetadata | undefined;
  onToggleProviderKey: (useWorkflowAIKey: boolean) => void;
  usesOwnKey: boolean;
};

function UpdateProviderModalContent(props: UpdateProviderModalContentProps) {
  const { providerMetadata, onToggleProviderKey, usesOwnKey } = props;
  const providerName = providerMetadata?.name;
  const providerSupported = providerMetadata?.providerSupported;
  const { openModal } = useQueryParamModal(PROVIDER_KEYS_MODAL_OPEN);

  const handleOpenProviderKeysModal = useCallback(() => {
    openModal();
  }, [openModal]);

  const onUseWorkflowAIKey = useCallback(async () => {
    await onToggleProviderKey(true);
  }, [onToggleProviderKey]);

  const onUseOwnKey = useCallback(async () => {
    await onToggleProviderKey(false);
  }, [onToggleProviderKey]);

  return (
    <div className='p-4 flex flex-col gap-4 text-black'>
      <div className='text-xsm font-semibold'>
        {`Choose whether you would like to user WorkflowAI’s ${providerName} Key or if
        you’d like to add your own.`}
      </div>
      <div className='flex items-center gap-2'>
        <ProviderSelectionCard
          icon={KeyMultipleFilled}
          title='Use WorkflowAI’s Provider Keys (recommended).'
          selected={!usesOwnKey}
          onClick={onUseWorkflowAIKey}
        />
        <ProviderSelectionCard
          icon={KeyFilled}
          title={`Use my own ${providerName} Key. ${!providerSupported ? '(Coming Soon!)' : ''}`}
          selected={usesOwnKey}
          disabled={!providerSupported}
          onClick={onUseOwnKey}
        />
      </div>
      <div className='text-gray-800 text-xs font-semibold'>
        You will be charged the same price using WorkflowAI’s keys as your own.
      </div>
      <Button variant='link' className='w-fit' onClick={handleOpenProviderKeysModal}>
        Manage Provider Keys
      </Button>
    </div>
  );
}

type UpdateProviderModalProps = {
  onClose: () => void;
  selectedVersion: VersionV1 | undefined;
  onToggleProviderKey: (useWorkflowAIKey: boolean) => void;
};

export function UpdateProviderModal(props: UpdateProviderModalProps) {
  const { onClose, selectedVersion, onToggleProviderKey } = props;

  const onOpenChange = useCallback(
    (open: boolean) => {
      if (!open) {
        onClose();
      }
    },
    [onClose]
  );

  const providerMetadata = useMemo(
    () => AI_PROVIDERS_METADATA[selectedVersion?.properties?.provider as Provider],
    [selectedVersion]
  );

  const usesOwnKey = !!selectedVersion?.deployments?.[0]?.provider_config_id;

  return (
    <Dialog open={!!selectedVersion} onOpenChange={onOpenChange}>
      <DialogContent className='flex flex-col p-0 gap-0 max-w-fit'>
        <DialogHeader
          title={`Update ${providerMetadata?.name} Provider Key Source for Version ${selectedVersion?.iteration}`}
          onClose={onClose}
        />
        <UpdateProviderModalContent
          providerMetadata={providerMetadata}
          onToggleProviderKey={onToggleProviderKey}
          usesOwnKey={usesOwnKey}
        />
      </DialogContent>
    </Dialog>
  );
}
