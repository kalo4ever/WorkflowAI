import { captureException } from '@sentry/nextjs';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  displayErrorToaster,
  displaySuccessToaster,
} from '@/components/ui/Sonner';
import { ImproveVersionResponse, useOrFetchToken, useTasks } from '@/store';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { ToolKind, VersionV1 } from '@/types/workflowAI';
import { RunTaskOptions } from './usePlaygroundPersistedState';
import { TaskRunner } from './useTaskRunners';

type ImproveTaskRunVersionProps = {
  taskId: TaskID;
  tenant: TenantID | undefined;
  taskSchemaId: TaskSchemaID;
  taskRunners: [TaskRunner, TaskRunner, TaskRunner];
  versionsForRuns: Record<string, VersionV1>;
  instructions: string;
  setInstructions: (instructions: string) => void;
  setImproveVersionChangelog: (changelog: string[] | undefined) => void;
  handleRunTasks: (options?: RunTaskOptions) => void;
};

export function useImproveTaskRunVersions(props: ImproveTaskRunVersionProps) {
  const {
    tenant,
    taskId,
    taskSchemaId,
    taskRunners,
    versionsForRuns,
    instructions,
    setInstructions,
    setImproveVersionChangelog,
    handleRunTasks,
  } = props;
  const improveVersion = useTasks((state) => state.improveVersion);
  const { token } = useOrFetchToken();

  const [oldInstructions, setOldInstructions] = useState<string | undefined>(
    undefined
  );

  const resetOldInstructions = useCallback(() => {
    setOldInstructions(undefined);
  }, []);

  const instructionsRef = useRef(instructions);

  useEffect(() => {
    instructionsRef.current = instructions;
  }, [instructions]);

  const [isImproveVersionLoading, setIsImproveVersionLoading] = useState(false);

  const improveTaskRunVersion = useCallback(
    async (taskRunId: string, userEvaluation: string, index: number) => {
      try {
        const onMessage = (message: ImproveVersionResponse) => {
          const { improved_properties, changelog } = message;
          setImproveVersionChangelog(changelog);
          const newInstructions = improved_properties.instructions || '';
          setInstructions(newInstructions);
        };
        setOldInstructions(instructionsRef.current);
        setIsImproveVersionLoading(true);
        const { improved_properties, changelog } = await improveVersion(
          tenant,
          taskId,
          {
            run_id: taskRunId,
            user_evaluation: userEvaluation,
          },
          token,
          onMessage
        );
        setImproveVersionChangelog(changelog);
        const newInstructions = improved_properties.instructions || '';
        setInstructions(newInstructions);
        displaySuccessToaster(
          'Updated Instructions generated. Rerunning AI agent...'
        );

        const taskRunGroup = taskRunners[index].data?.group;
        if (!taskRunGroup) {
          return;
        }

        const versionId = taskRunners[index].data?.group.id;
        if (!versionId) {
          return;
        }

        const version = versionsForRuns[versionId];
        if (!version) {
          return;
        }

        setIsImproveVersionLoading(false);

        handleRunTasks({
          externalVersion: {
            ...version,
            properties: {
              ...version.properties,
              instructions: newInstructions,
            },
          },
        });
      } catch (error) {
        captureException(error);
        displayErrorToaster(
          'Failed to improve AI agent run version - Please try again'
        );
        throw new Error('Failed to improve AI agent run version');
      }
    },
    [
      improveVersion,
      taskId,
      tenant,
      taskRunners,
      setInstructions,
      handleRunTasks,
      setImproveVersionChangelog,
      token,
      versionsForRuns,
    ]
  );

  const updateTaskInstructions = useTasks(
    (state) => state.updateTaskInstructions
  );

  const handleUpdateTaskInstructions = useCallback(
    async (tools: ToolKind[]) => {
      setOldInstructions(instructionsRef.current);
      setIsImproveVersionLoading(true);

      try {
        const data = await updateTaskInstructions(
          tenant,
          taskId,
          taskSchemaId,
          token,
          instructions,
          tools,
          setInstructions
        );
        setInstructions(data);
      } catch (error) {
        captureException(error);
        displayErrorToaster(
          'Failed to update AI Agent instructions - Please try again'
        );
        throw new Error('Failed to update AI Agent instructions');
      }

      setIsImproveVersionLoading(false);
    },
    [
      instructions,
      updateTaskInstructions,
      tenant,
      taskId,
      taskSchemaId,
      token,
      setInstructions,
    ]
  );

  return {
    isImproveVersionLoading,
    oldInstructions,
    resetOldInstructions,
    improveTaskRunVersion,
    updateTaskInstructions: handleUpdateTaskInstructions,
  };
}
