import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/Dialog';
import { displayErrorToaster, displaySuccessToaster } from '@/components/ui/Sonner';
import { DEPLOY_ITERATION_MODAL_OPEN, useQueryParamModal } from '@/lib/globalModal';
import { useIsAllowed } from '@/lib/hooks/useIsAllowed';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { useParsedSearchParams, useRedirectWithParams } from '@/lib/queryString';
import { taskApiRoute } from '@/lib/routeFormatter';
import { formatSemverVersion } from '@/lib/versionUtils';
import { useOrFetchVersions } from '@/store';
import { useReviewBenchmark } from '@/store/task_review_benchmark';
import { useVersions } from '@/store/versions';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { VersionEnvironment } from '@/types/workflowAI';
import { DeployVersionConfirmModal } from './DeployVersionConfirmModal';
import { DeployVersionContent } from './DeployVersionContent';

export function useEnvDeploy(tenant: TenantID, taskId: TaskID, taskSchemaId: TaskSchemaID | undefined) {
  const deployVersion = useVersions((state) => state.deployVersion);
  const redirectWithParams = useRedirectWithParams();

  const deployGroupToEnv = useCallback(
    async (
      environment: VersionEnvironment,
      versionId: string | undefined,
      versionText: string | undefined,
      redirectToCodeAfterDeploy?: boolean
    ) => {
      if (!taskSchemaId || !versionId) {
        return;
      }
      try {
        await deployVersion(tenant, taskId, versionId, {
          environment,
        });

        if (redirectToCodeAfterDeploy) {
          redirectWithParams({
            params: {
              selectedVersionId: versionId,
              selectedEnvironment: environment,
              deployIterationModalOpen: undefined,
              deployVersionId: undefined,
              deploySchemaId: undefined,
              redirectToCodeAfterDeploy: undefined,
            },
            path: taskApiRoute(tenant, taskId, taskSchemaId),
          });
        }

        displaySuccessToaster(
          <span>
            {`Version ${versionText} successfully deployed to ${environment}`}
            <br />
            <Link
              href={taskApiRoute(tenant, taskId, taskSchemaId, {
                selectedVersionId: versionId,
                selectedEnvironment: environment,
              })}
              className='underline cursor-pointer'
              onClick={(e) => e.stopPropagation()}
            >
              View Code
            </Link>
          </span>
        );
      } catch (e: unknown) {
        displayErrorToaster('Failed to deploy');
      }
    },
    [deployVersion, tenant, taskId, taskSchemaId, redirectWithParams]
  );

  return deployGroupToEnv;
}

type NewTaskModalQueryParams = {
  deployVersionId: string | undefined;
  deploySchemaId: TaskSchemaID | undefined;
  redirectToCodeAfterDeploy: 'true' | undefined;
};

const searchParams: (keyof NewTaskModalQueryParams)[] = [
  'deployVersionId',
  'deploySchemaId',
  'redirectToCodeAfterDeploy',
];

export function useDeployVersionModal() {
  const { open, openModal, closeModal } = useQueryParamModal<NewTaskModalQueryParams>(
    DEPLOY_ITERATION_MODAL_OPEN,
    searchParams
  );

  const onDeployToClick = useCallback(
    (versionId: string | undefined, schemaId?: TaskSchemaID, redirectToCodeAfterDeploy?: boolean) => {
      if (versionId === undefined) {
        return;
      }
      openModal({
        deployVersionId: versionId,
        deploySchemaId: schemaId,
        redirectToCodeAfterDeploy: !!redirectToCodeAfterDeploy ? 'true' : undefined,
      });
    },
    [openModal]
  );

  return { open, openModal, closeModal, onDeployToClick };
}

export function DeployVersionModal() {
  const { tenant, taskId, taskSchemaId: paramsTaskSchemaId } = useTaskSchemaParams();
  const { open, closeModal: onClose } = useDeployVersionModal();

  const {
    deployVersionId: currentVersionId,
    deploySchemaId,
    redirectToCodeAfterDeploy: redirectToCodeAfterDeployText,
  } = useParsedSearchParams('deployVersionId', 'deploySchemaId', 'redirectToCodeAfterDeploy');

  const [selectedEnvironment, setSelectedEnvironment] = useState<VersionEnvironment | undefined>(undefined);

  const redirectToCodeAfterDeploy = redirectToCodeAfterDeployText === 'true';

  const taskSchemaId = (deploySchemaId as TaskSchemaID) ?? paramsTaskSchemaId;

  const { versions, isInitialized, versionsPerEnvironment } = useOrFetchVersions(tenant, taskId, taskSchemaId);

  const { checkIfAllowed } = useIsAllowed();

  useEffect(() => {
    if (open && !checkIfAllowed()) {
      onClose();
    }
  }, [open, checkIfAllowed, onClose]);

  const currentVersion = useMemo(
    () => versions.find((version) => version.id === currentVersionId),
    [versions, currentVersionId]
  );

  const currentIteration = currentVersion?.iteration;

  const updateBenchmark = useReviewBenchmark((state) => state.updateBenchmark);

  const onCancel = useCallback(() => {
    setSelectedEnvironment(undefined);
  }, []);

  useEffect(() => {
    if (!open) {
      setSelectedEnvironment(undefined);
    }
  }, [open]);

  const deployVersionToEnv = useEnvDeploy(tenant, taskId, taskSchemaId);

  const versionText = formatSemverVersion(currentVersion);

  const handleDeploy = useCallback(async () => {
    if (!selectedEnvironment) {
      return;
    }

    await deployVersionToEnv(selectedEnvironment, currentVersionId, versionText, redirectToCodeAfterDeploy);

    if (currentIteration !== undefined) {
      await updateBenchmark(tenant, taskId, taskSchemaId, [currentIteration], []);
    }

    if (!redirectToCodeAfterDeploy) {
      onClose();
    }
  }, [
    currentIteration,
    currentVersionId,
    deployVersionToEnv,
    onClose,
    redirectToCodeAfterDeploy,
    taskId,
    taskSchemaId,
    updateBenchmark,
    tenant,
    versionText,
    selectedEnvironment,
  ]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className='p-0 max-w-[800px] w-auto overflow-hidden bg-custom-gradient-1'>
        <DeployVersionContent
          version={currentVersion}
          onClose={onClose}
          isInitialized={isInitialized}
          versionsPerEnvironment={versionsPerEnvironment}
          selectedEnvironment={selectedEnvironment}
          setSelectedEnvironment={setSelectedEnvironment}
        />
        <DeployVersionConfirmModal
          showConfirmModal={!!selectedEnvironment}
          versionBadgeText={formatSemverVersion(currentVersion)}
          closeModal={onCancel}
          onConfirm={handleDeploy}
        />
      </DialogContent>
    </Dialog>
  );
}
