'use client';

import { useCallback, useState } from 'react';
import {
  PROVIDER_KEYS_MODAL_OPEN,
  useQueryParamModal,
} from '@/lib/globalModal';
import { useOrFetchOrganizationSettings } from '@/store';
import { useOrganizationSettings } from '@/store/organization_settings';
import { AI_PROVIDERS_METADATA } from '../AIModelsCombobox/utils';
import { Button } from '../ui/Button';
import { Dialog, DialogContent } from '../ui/Dialog';
import { AddProviderKeyModal } from './AddProviderKeyModal';
import { ProviderKeyManagementItem } from './ProviderKeyManagementItem';

export function ManageProviderKeysModal() {
  const { open, closeModal } = useQueryParamModal(PROVIDER_KEYS_MODAL_OPEN);
  const [currentProvider, setCurrentProvider] = useState<
    string | null | undefined
  >(null);
  const onCloseAddProviderKeyModal = useCallback(() => {
    setCurrentProvider(null);
  }, [setCurrentProvider]);

  const addProviderConfig = useOrganizationSettings(
    (state) => state.addProviderConfig
  );

  const deleteProviderConfig = useOrganizationSettings(
    (state) => state.deleteProviderConfig
  );

  const { organizationSettings } = useOrFetchOrganizationSettings();

  const onOpenChange = useCallback(
    (open: boolean) => {
      if (!open) {
        closeModal();
      }
    },
    [closeModal]
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='p-0 gap-0 max-h-[528px] max-w-[400px] bg-custom-gradient-1 flex flex-col overflow-hidden'>
        <div className='flex flex-col gap-3.5 px-4 py-3.5 border-b border-gray-200 border-dashed'>
          <div className='text-[16px] font-semibold text-gray-900'>
            Manage Provider Keys
          </div>
          <div className='text-gray-900 text-[12px] font-normal'>
            If you prefer to use your own API keys for specific providers, you
            can add them here.
          </div>
          <div className='text-gray-900 text-[12px] font-normal'>
            Your API keys will take priority when deciding on model providers to
            user, however WorkflowAI’s keys may be used as a backup if yours hit
            a rate limit.
          </div>
        </div>

        <div className='p-0 flex flex-col overflow-y-auto px-4'>
          {Object.entries(AI_PROVIDERS_METADATA).map(([provider, metadata]) => (
            <ProviderKeyManagementItem
              key={metadata.name}
              settingsProviders={organizationSettings?.providers}
              provider={provider}
              providerMetadata={metadata}
              setCurrentProvider={setCurrentProvider}
              deleteProviderConfig={deleteProviderConfig}
            />
          ))}
        </div>

        <div className='justify-between items-center flex px-4 py-3'>
          <Button variant='newDesignGray' onClick={closeModal}>
            Cancel
          </Button>
          <Button variant='newDesignIndigo' onClick={closeModal}>
            Done
          </Button>
        </div>

        <AddProviderKeyModal
          open={!!currentProvider}
          onClose={onCloseAddProviderKeyModal}
          currentProvider={currentProvider}
          organizationSettings={organizationSettings}
          addProviderConfig={addProviderConfig}
        />
      </DialogContent>
    </Dialog>
  );
}
