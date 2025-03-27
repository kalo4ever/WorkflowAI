import { format } from 'date-fns';
import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { TaskStats, TaskStatsResponse } from '@/types/workflowAI';
import { buildTaskStatsScopeKey, taskSubPath } from './utils';

enableMapSet();

interface TaskStatsState {
  taskStatsByScope: Map<string, TaskStats[]>;
  isInitializedByScope: Map<string, boolean>;
  isLoadingByScope: Map<string, boolean>;

  fetchTaskStats(
    tenant: TenantID | undefined,
    taskId: TaskID,
    createdAfter?: Date,
    createdBefore?: Date,
    taskSchemaId?: TaskSchemaID,
    version?: string,
    isActive?: boolean
  ): Promise<TaskStats[] | undefined>;
}

export const useTaskStats = create<TaskStatsState>((set, get) => ({
  taskStatsByScope: new Map<string, TaskStats[]>(),
  isInitializedByScope: new Map<string, boolean>(),
  isLoadingByScope: new Map<string, boolean>(),

  fetchTaskStats: async (
    tenant: TenantID | undefined,
    taskId: TaskID,
    createdAfter?: Date,
    createdBefore?: Date,
    taskSchemaId?: TaskSchemaID,
    versionID?: string,
    isActive?: boolean
  ) => {
    const scope = buildTaskStatsScopeKey({
      tenant,
      taskId,
      createdAfter,
      createdBefore,
      taskSchemaId,
      versionID,
      isActive,
    });
    if (get().isLoadingByScope.get(scope)) {
      return;
    }
    set(
      produce((state: TaskStatsState) => {
        state.isLoadingByScope.set(scope, true);
      })
    );

    let result: TaskStats[] | undefined = undefined;

    try {
      const queryParams = new URLSearchParams();

      if (createdAfter) {
        queryParams.append('created_after', format(createdAfter, "yyyy-MM-dd'T'HH:mm:ss.SSSxxx"));
      }

      if (createdBefore) {
        queryParams.append('created_before', format(createdBefore, "yyyy-MM-dd'T'HH:mm:ss.SSSxxx"));
      }

      if (taskSchemaId) {
        queryParams.append('task_schema_id', taskSchemaId);
      }

      if (versionID) {
        queryParams.append('version_id', versionID);
      }

      if (isActive) {
        queryParams.append('is_active', isActive.toString());
      }

      const queryString = queryParams.toString();
      const url = taskSubPath(tenant, taskId, `/runs/stats${queryString ? `?${queryString}` : ''}`);

      const { data: taskStats } = await client.get<TaskStatsResponse>(url);
      set(
        produce((state) => {
          state.taskStatsByScope.set(scope, taskStats);
        })
      );
      result = taskStats;
    } catch (error) {
      console.error('Failed to fetch AI agents runs', error);
    }
    set(
      produce((state: TaskStatsState) => {
        state.isInitializedByScope.set(scope, true);
        state.isLoadingByScope.set(scope, false);
      })
    );

    return result;
  },
}));
