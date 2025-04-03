'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useEnvDeploy } from '@/components/DeployIterationModal/DeployVersionModal';
import { AddProviderKeyModal } from '@/components/ProviderKeysModal/AddProviderKeyModal';
import { useFindProviderConfigID } from '@/components/ProviderKeysModal/useFindProviderConfigID';
import { Button } from '@/components/ui/Button';
import { PageContainer } from '@/components/v2/PageContainer';
import { PROVIDER_KEYS_MODAL_OPEN, useQueryParamModal } from '@/lib/globalModal';
import { useDemoMode } from '@/lib/hooks/useDemoMode';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { formatSemverVersion } from '@/lib/versionUtils';
import { useOrFetchOrganizationSettings, useOrFetchTask, useOrFetchVersions } from '@/store';
import { useOrganizationSettings } from '@/store/organization_settings';
import { useVersions } from '@/store/versions';
import { TaskSchemaID } from '@/types/aliases';
import { Model, VersionV1 } from '@/types/workflowAI';
import { DeployVersionModal, EditEnvSchemaIterationParams } from './DeployVersionModal';
import { EnvironmentDeployment } from './EnvironmentDeployment';
import { UpdateProviderModal } from './UpdateProviderModal';

export function DeploymentsContainer() {
  const { tenant, taskId, taskSchemaId } = useTaskSchemaParams();
  const { task, isInitialized: isTaskInitialized } = useOrFetchTask(tenant, taskId);

  const {
    versions,
    deployedVersions,
    versionsPerEnvironment,
    isInitialized: isVersionsInitialized,
  } = useOrFetchVersions(tenant, taskId);

  const fetchVersions = useVersions((state) => state.fetchVersions);

  const [envSchemaIteration, setEnvSchemaIteration] = useState<EditEnvSchemaIterationParams | undefined>();

  const onCloseEnvSchemaIteration = useCallback(() => setEnvSchemaIteration(undefined), [setEnvSchemaIteration]);

  const [selectedVersion, setSelectedVersion] = useState<VersionV1 | undefined>();

  const onCloseUpdateProviderModal = useCallback(() => setSelectedVersion(undefined), [setSelectedVersion]);

  const [addProviderKeyModalOpen, setAddProviderKeyModalOpen] = useState(false);
  const onCloseAddProviderKeyModal = useCallback(() => setAddProviderKeyModalOpen(false), [setAddProviderKeyModalOpen]);

  const { organizationSettings, isInitialized: isOrganizationSettingsInitialized } = useOrFetchOrganizationSettings();

  const addProviderConfig = useOrganizationSettings((state) => state.addProviderConfig);

  const model: Model | string | undefined = selectedVersion?.model;

  const { providerConfigID: settingsProviderConfigID } = useFindProviderConfigID({
    tenant,
    taskId,
    taskSchemaId,
    providerSettings: organizationSettings?.providers,
    model: model,
  });

  const deployVersion = useVersions((state) => state.deployVersion);
  const environment = selectedVersion?.deployments?.[0]?.environment;

  const onToggleProviderKey = useCallback(
    async (useWorkflowAIKey: boolean) => {
      if (!selectedVersion?.schema_id || !selectedVersion.iteration || !environment) {
        return;
      }

      if (!useWorkflowAIKey && !settingsProviderConfigID) {
        setAddProviderKeyModalOpen(true);
        return;
      }

      const payload = {
        environment,
        provider_config_id: useWorkflowAIKey ? undefined : settingsProviderConfigID,
      };

      const newSelectedVersion = await deployVersion(
        tenant,
        taskId,
        selectedVersion.schema_id?.toString() as TaskSchemaID,
        selectedVersion.id,
        selectedVersion.iteration,
        payload
      );

      setSelectedVersion(newSelectedVersion);
    },
    [deployVersion, tenant, taskId, settingsProviderConfigID, environment, selectedVersion]
  );

  const [shouldToggleProviderKey, setShouldToggleProviderKey] = useState(false);
  const handleAddProviderKeyModalClose = useCallback(
    (keyWasAdded: boolean) => {
      if (keyWasAdded) {
        setShouldToggleProviderKey(true);
      }
      onCloseAddProviderKeyModal();
    },
    [onCloseAddProviderKeyModal]
  );
  useEffect(() => {
    if (shouldToggleProviderKey && !!settingsProviderConfigID) {
      onToggleProviderKey(false);
      setShouldToggleProviderKey(false);
    }
  }, [shouldToggleProviderKey, onToggleProviderKey, settingsProviderConfigID]);

  const favoriteVersions = useMemo(() => versions.filter((version) => version.is_favorite), [versions]);

  const deployVersionToEnv = useEnvDeploy(
    tenant,
    taskId,
    envSchemaIteration?.schemaId?.toString() as TaskSchemaID | undefined
  );

  const onDeploy = useCallback(async () => {
    if (!envSchemaIteration) {
      return;
    }

    const version = versions.find((version) => version.iteration.toString() === envSchemaIteration.iteration);

    const versionId = version?.id;
    const versionText = formatSemverVersion(version);

    if (!versionId) {
      return;
    }

    const providerConfigId = !!envSchemaIteration.currentIteration
      ? deployedVersions.find((version) => version?.iteration?.toString() === envSchemaIteration.iteration?.toString())
          ?.deployments?.[0]?.provider_config_id
      : undefined;

    await deployVersionToEnv(
      envSchemaIteration.environment,
      versionId,
      versionText,
      envSchemaIteration?.iteration,
      providerConfigId
    );

    await fetchVersions(tenant, taskId, undefined);
    onCloseEnvSchemaIteration();
  }, [
    deployVersionToEnv,
    envSchemaIteration,
    fetchVersions,
    tenant,
    taskId,
    onCloseEnvSchemaIteration,
    deployedVersions,
    versions,
  ]);

  const onIterationChange = useCallback(
    (iteration: string) => {
      if (!envSchemaIteration) {
        return;
      }
      setEnvSchemaIteration({ ...envSchemaIteration, iteration });
    },
    [setEnvSchemaIteration, envSchemaIteration]
  );

  const { openModal: openProviderKeysModal } = useQueryParamModal(PROVIDER_KEYS_MODAL_OPEN);

  const handleOpenProviderKeysModal = useCallback(() => {
    openProviderKeysModal();
  }, [openProviderKeysModal]);

  const { isInDemoMode } = useDemoMode();

  const commonProps = {
    tenant,
    taskId,
    setEnvSchemaIteration,
    setSelectedVersion,
    taskSchemaId,
    versionsPerEnvironment,
    isInDemoMode,
  };

  return (
    <PageContainer
      name='Deployments'
      task={task}
      showSchema={false}
      isInitialized={isTaskInitialized && isVersionsInitialized && isOrganizationSettingsInitialized}
      documentationLink='https://docs.workflowai.com/features/deployments'
      rightBarChildren={
        <div className='flex flex-row items-center gap-2 font-lato'>
          <Button variant='newDesign' onClick={handleOpenProviderKeysModal} className='min-h-8' disabled={isInDemoMode}>
            Manage Provider Keys
          </Button>
        </div>
      }
    >
      <div className='flex flex-col h-full w-full overflow-y-auto font-lato'>
        <EnvironmentDeployment
          environment={'production'}
          versions={versionsPerEnvironment?.production}
          {...commonProps}
        />
        <EnvironmentDeployment environment={'staging'} versions={versionsPerEnvironment?.staging} {...commonProps} />
        <EnvironmentDeployment environment={'dev'} versions={versionsPerEnvironment?.dev} {...commonProps} />
      </div>
      <DeployVersionModal
        envSchemaIteration={envSchemaIteration}
        setEnvSchemaIteration={setEnvSchemaIteration}
        onClose={onCloseEnvSchemaIteration}
        onDeploy={onDeploy}
        onIterationChange={onIterationChange}
        isInitialized={isVersionsInitialized}
        favoriteVersions={favoriteVersions}
        allVersions={versions}
        tenant={tenant}
        taskId={taskId}
      />
      <UpdateProviderModal
        selectedVersion={selectedVersion}
        onClose={onCloseUpdateProviderModal}
        onToggleProviderKey={onToggleProviderKey}
      />
      <AddProviderKeyModal
        open={addProviderKeyModalOpen}
        onClose={handleAddProviderKeyModalClose}
        currentProvider={selectedVersion?.properties?.provider}
        organizationSettings={organizationSettings}
        addProviderConfig={addProviderConfig}
      />
    </PageContainer>
  );
}
