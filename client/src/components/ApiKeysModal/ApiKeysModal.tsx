'use client';

import { PlusIcon } from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { API_KEYS_MODAL_OPEN } from '@/lib/globalModal';
import { useQueryParamModal } from '@/lib/globalModal';
import {
  useLoggedInTenantID,
  useTaskSchemaParams,
} from '@/lib/hooks/useTaskParams';
import { TENANT_PLACEHOLDER } from '@/lib/routeFormatter';
import { useOrFetchApiKeys, useOrFetchClerkUsers } from '@/store';
import { useApiKeys } from '@/store/api_keys';
import { TenantID } from '@/types/aliases';
import { useAuth } from '../../lib/AuthContext';
import { Button } from '../ui/Button';
import { Dialog, DialogContent, DialogHeader } from '../ui/Dialog';
import { ApiKeysTable } from './ApiKeysTable';
import { NewApiKeyModal } from './NewApiKeyModal';

export function useApiKeysModal() {
  return useQueryParamModal<{ apiKeysModalOpen: string | undefined }>(
    API_KEYS_MODAL_OPEN
  );
}

type ApiKeysModalProps = {
  open?: boolean;
  closeModal?: () => void;
  showClose?: boolean;
};

export function ApiKeysModal(props: ApiKeysModalProps) {
  const {
    open: openFromProps,
    closeModal: closeModalFromProps,
    showClose = true,
  } = props;

  const { user } = useAuth();
  const isLogged = !!user;

  const { tenant: tenantFromParams } = useTaskSchemaParams();
  const loggedInTenant = useLoggedInTenantID();

  const tenant = useMemo(() => {
    if (tenantFromParams !== TENANT_PLACEHOLDER) {
      return tenantFromParams;
    }
    return loggedInTenant ?? (TENANT_PLACEHOLDER as TenantID);
  }, [tenantFromParams, loggedInTenant]);

  const { open: openFromHook, closeModal: closeModalFromHook } =
    useApiKeysModal();

  const open = openFromProps ?? openFromHook;
  const closeModal = closeModalFromProps ?? closeModalFromHook;

  const { createApiKey, deleteApiKey } = useApiKeys();

  const { apiKeys, isInitialized } = useOrFetchApiKeys(tenant);
  const userIds = useMemo(() => {
    const result = new Set<string>();
    apiKeys.forEach((apiKey) => {
      if (apiKey.created_by?.user_id) {
        result.add(apiKey.created_by.user_id);
      }
    });
    return Array.from(result);
  }, [apiKeys]);
  const { usersByID } = useOrFetchClerkUsers(userIds);

  const [newApiKeyModalOpen, setNewApiKeyModalOpen] = useState(false);
  const toggleNewApiKeyModal = useCallback(
    () => setNewApiKeyModalOpen(!newApiKeyModalOpen),
    [newApiKeyModalOpen]
  );

  const hasOpenedNewApiKeyModalIfNeeded = useRef(false);
  useEffect(() => {
    if (!isInitialized || !open) {
      setNewApiKeyModalOpen(false);
      hasOpenedNewApiKeyModalIfNeeded.current = false;
      return;
    }
    if (
      apiKeys.length === 0 &&
      !hasOpenedNewApiKeyModalIfNeeded.current &&
      isLogged
    ) {
      setNewApiKeyModalOpen(true);
    }
    hasOpenedNewApiKeyModalIfNeeded.current = true;
  }, [isInitialized, apiKeys.length, open, isLogged]);

  const onCreate = useCallback(
    (name: string) => createApiKey(tenant, name),
    [createApiKey, tenant]
  );

  const onDelete = useCallback(
    (id: string) => deleteApiKey(tenant, id),
    [deleteApiKey, tenant]
  );

  if (!isInitialized) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={closeModal}>
      <DialogContent className='p-0 flex flex-col gap-0 min-h-[50vh] w-fit max-h-[90vh] max-w-[90vw]'>
        <DialogHeader
          title='Secret Keys'
          onClose={showClose ? closeModal : undefined}
        >
          <Button
            variant='newDesign'
            onClick={toggleNewApiKeyModal}
            lucideIcon={PlusIcon}
            disabled={!isLogged}
          >
            New Secret Key
          </Button>
        </DialogHeader>

        <div className='flex-1 flex flex-col p-4 overflow-hidden'>
          <ApiKeysTable
            apiKeys={apiKeys}
            usersByID={usersByID}
            onDelete={onDelete}
            isLogged={isLogged}
          />
        </div>

        <NewApiKeyModal
          open={newApiKeyModalOpen}
          onClose={toggleNewApiKeyModal}
          onCreate={onCreate}
        />
      </DialogContent>
    </Dialog>
  );
}
