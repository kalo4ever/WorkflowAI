'use client';

import { useCallback, useMemo, useState } from 'react';
import { useDeployVersionModal } from '@/components/DeployIterationModal/DeployVersionModal';
import {
  DEFAULT_TASK_VERSION_EDITABLE_PROPERTIES,
  NewGroupModal,
  TaskVersionEditableProperties,
} from '@/components/NewVersionModal';
import { Loader } from '@/components/ui/Loader';
import { useCompatibleAIModels } from '@/lib/hooks/useCompatibleAIModels';
import { useDemoMode } from '@/lib/hooks/useDemoMode';
import { useRedirectWithParams } from '@/lib/queryString';
import {
  TaskSchemaParams,
  taskApiRoute,
  taskSchemaRoute,
} from '@/lib/routeFormatter';
import { cn } from '@/lib/utils';
import {
  sortEnvironmentsInOrderOfImportance,
  sortVersions,
  sortVersionsByEnvironment,
} from '@/lib/versionUtils';
import { environmentsForVersion } from '@/lib/versionUtils';
import { useOrFetchClerkUsers } from '@/store';
import { getVersionsPerEnvironment, useVersions } from '@/store/versions';
import { UNDEFINED_MODEL } from '@/types/aliases';
import { VersionEnvironment, VersionV1 } from '@/types/workflowAI';
import { TaskVersionEntry } from './TaskVersionEntry';
import { TaskVersionsHeader } from './TaskVersionsHeader';
import { VersionAvatarType } from './utils';

export type TaskVersionsContainerProps = TaskSchemaParams & {
  avatarType?: VersionAvatarType;
  areVersionsInitialized: boolean;
  versionsToShow: VersionV1[];
  className?: string;
  showHeader?: boolean;
  showGroupActions?: boolean;
  selectedIteration?: string | null;
  onIterationChange?: (iteration: string) => void;
  smallMode?: boolean;
  sort?: 'environment' | 'version';
};

export function TaskVersionsContainer(props: TaskVersionsContainerProps) {
  const {
    avatarType = VersionAvatarType.Created,
    areVersionsInitialized,
    tenant,
    taskId,
    taskSchemaId,
    versionsToShow: versions,
    className,
    showHeader = true,
    showGroupActions = false,
    selectedIteration,
    onIterationChange,
    smallMode = false,
    sort = 'environment',
  } = props;

  const { onDeployToClick } = useDeployVersionModal();

  const [newGroupModalOpen, setNewGroupModalOpen] = useState(false);

  const versionsPerEnvironment = useMemo(
    () => getVersionsPerEnvironment(versions),
    [versions]
  );

  const userIds = useMemo(() => {
    const result = new Set<string>();
    versions.forEach((version) => {
      if (version.created_by?.user_id) {
        result.add(version.created_by.user_id);
      }

      if (version.favorited_by?.user_id) {
        result.add(version.favorited_by.user_id);
      }

      version.deployments?.forEach((deployment) => {
        if (deployment.deployed_by?.user_id) {
          result.add(deployment.deployed_by.user_id);
        }
      });
    });
    return Array.from(result);
  }, [versions]);

  const { usersByID } = useOrFetchClerkUsers(userIds);

  const versionIdsAndEnvironmentsDict = useMemo(() => {
    if (!versionsPerEnvironment) {
      return undefined;
    }

    const dict: Record<string, VersionEnvironment[]> = {};

    Object.entries(versionsPerEnvironment).forEach(
      ([environment, versions]) => {
        if (!versions) {
          return;
        }
        versions.forEach((version) => {
          if (!version.id) {
            return;
          }
          if (!dict[version.id]) {
            dict[version.id] = [];
          }
          dict[version.id].push(environment as VersionEnvironment);
        });
      }
    );

    Object.keys(dict).forEach((key) => {
      dict[key] = sortEnvironmentsInOrderOfImportance(dict[key]);
    });

    return dict;
  }, [versionsPerEnvironment]);

  const sortedVersions = useMemo(() => {
    if (sort === 'environment') {
      return sortVersionsByEnvironment(versions, versionIdsAndEnvironmentsDict);
    }
    return sortVersions(versions);
  }, [versions, versionIdsAndEnvironmentsDict, sort]);

  const createVersion = useVersions((state) => state.createVersion);
  const saveVersion = useVersions((state) => state.saveVersion);

  // TODO: this is a duplicate from benchmarks container we should wrap the callback in a custom tool
  const addOrReuseVersion = useCallback(
    async (properties: TaskVersionEditableProperties) => {
      if (!properties.modelId) return false;

      const result = await createVersion(tenant, taskId, taskSchemaId, {
        properties: {
          model: properties.modelId,
          instructions: properties.instructions,
          temperature: properties.temperature,
          task_variant_id: properties.variantId,
        },
      });
      await saveVersion(tenant, taskId, result.id);
      return true;
    },
    [createVersion, saveVersion, tenant, taskId, taskSchemaId]
  );

  const redirectWithParams = useRedirectWithParams();

  const onTryInPlayground = useCallback(
    (versionId: string | undefined, variantId: string | undefined) => {
      if (!versionId) return;
      redirectWithParams({
        path: taskSchemaRoute(tenant, taskId, taskSchemaId, {
          versionId,
          preselectedVariantId: variantId,
        }),
      });
    },
    [redirectWithParams, tenant, taskId, taskSchemaId]
  );

  const onViewCode = useCallback(
    (version: VersionV1) => {
      if (!version.id) return;
      const environments = environmentsForVersion(version);
      redirectWithParams({
        path: taskApiRoute(tenant, taskId, taskSchemaId),
        params: {
          selectedVersionId: version.id,
          selectedEnvironment: environments?.[0],
        },
      });
    },
    [redirectWithParams, tenant, taskId, taskSchemaId]
  );

  const [editableProperties, setEditableProperties] =
    useState<TaskVersionEditableProperties>(
      DEFAULT_TASK_VERSION_EDITABLE_PROPERTIES
    );

  const { compatibleModels: models } = useCompatibleAIModels({
    tenant,
    taskId,
    taskSchemaId,
  });

  const handleCloneVersion = useCallback(
    (version: VersionV1) => {
      const { properties } = version;
      const newEditableProperties: TaskVersionEditableProperties = {
        instructions: properties.instructions ?? '',
        temperature: properties.temperature ?? 0,
        // We don't want to clone the modelId on purpose to avoid reusing the same model
        modelId: UNDEFINED_MODEL,
        variantId: properties.task_variant_id ?? '',
      };
      setEditableProperties(newEditableProperties);
      setNewGroupModalOpen(true);
    },
    [setNewGroupModalOpen]
  );

  const closeNewGroupModal = useCallback(() => {
    setNewGroupModalOpen(false);
  }, []);

  const { isInDemoMode } = useDemoMode();

  if (!areVersionsInitialized) {
    return <Loader centered />;
  }

  return (
    <div className={cn('flex flex-row w-full overflow-clip', className)}>
      {sortedVersions.length === 0 && (
        <div className='h-[148px] w-full flex flex-col items-center justify-center px-4 py-3 bg-slate-100 rounded-[20px] text-slate-400 text-[16px]'>
          <div>
            Click <span className='font-semibold'>Add New Version</span> to
            create a new version.
          </div>
        </div>
      )}
      <div className='flex flex-col w-full border border-gray-200 rounded-[2px] px-2 pb-2 bg-gradient-to-b from-white/50 to-white/20'>
        {showHeader && <TaskVersionsHeader smallMode={smallMode} />}
        {sortedVersions.map((version) => (
          <TaskVersionEntry
            key={version.id}
            version={version}
            avatarType={avatarType}
            usersByID={usersByID}
            onClone={() => handleCloneVersion(version)}
            onTryInPlayground={() =>
              onTryInPlayground(
                version.id,
                version.properties.task_variant_id ?? undefined
              )
            }
            onViewCode={() => onViewCode(version)}
            onDeploy={() => onDeployToClick(version.id)}
            showGroupActions={showGroupActions}
            isSelected={`${version.iteration}` === selectedIteration}
            onSelect={
              selectedIteration !== undefined ? onIterationChange : undefined
            }
            smallMode={smallMode}
            isInDemoMode={isInDemoMode}
          />
        ))}
      </div>
      <NewGroupModal
        tenant={tenant}
        taskId={taskId}
        taskSchemaId={taskSchemaId}
        open={newGroupModalOpen}
        onClose={closeNewGroupModal}
        addOrReuseVersion={addOrReuseVersion}
        versionWasNotAddedAlertTitle='Version Already Benchmarked'
        versionWasNotAddedAlertBody='Looks like this version already exists in your benchmark! No need to create another.'
        models={models}
        editableProperties={editableProperties}
        setEditableProperties={setEditableProperties}
      />
    </div>
  );
}
