import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { TaskSchemaResponseWithSchema } from '@/types/task';
import {
  TaskSchemaResponse,
  TaskSchemaUpdateRequest,
} from '@/types/workflowAI';
import { useTasks } from './task';
import { buildScopeKey, taskSchemaSubPath } from './utils';

enableMapSet();

interface TaskVersionsState {
  taskSchemasByScope: Map<string, TaskSchemaResponseWithSchema>;
  isTaskSchemaLoadingByScope: Map<string, boolean>;
  isTaskSchemaInitializedByScope: Map<string, boolean>;
  fetchTaskSchema: (
    tenant: TenantID | undefined,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID
  ) => Promise<void>;
  changeTaskSchemaVisibility: (
    tenant: TenantID | undefined,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID,
    isVisible: boolean
  ) => Promise<void>;
}

export const useTaskSchemas = create<TaskVersionsState>((set, get) => ({
  taskSchemasByScope: new Map<string, TaskSchemaResponseWithSchema>(),
  isTaskSchemaLoadingByScope: new Map<string, boolean>(),
  isTaskSchemaInitializedByScope: new Map<string, boolean>(),
  fetchTaskSchema: async (tenant, taskId, taskSchemaId) => {
    const scope = buildScopeKey({ tenant, taskId, taskSchemaId });
    if (get().isTaskSchemaLoadingByScope.get(scope)) return;
    set(
      produce<TaskVersionsState>((state) => {
        state.isTaskSchemaLoadingByScope.set(scope, true);
      })
    );
    try {
      const taskSchema = await client.get<TaskSchemaResponseWithSchema>(
        taskSchemaSubPath(tenant, taskId, taskSchemaId, '')
      );
      set(
        produce<TaskVersionsState>((state) => {
          state.taskSchemasByScope.set(scope, taskSchema);
        })
      );
    } catch (error) {
      console.error('Failed to fetch single AI agent version', error);
    }
    set(
      produce<TaskVersionsState>((state) => {
        state.isTaskSchemaLoadingByScope.set(scope, false);
        state.isTaskSchemaInitializedByScope.set(scope, true);
      })
    );
  },

  changeTaskSchemaVisibility: async (
    tenant,
    taskId,
    taskSchemaId,
    isVisible
  ) => {
    try {
      await client.patch<TaskSchemaUpdateRequest, TaskSchemaResponse>(
        taskSchemaSubPath(tenant, taskId, taskSchemaId, ''),
        {
          is_hidden: !isVisible,
        }
      );
      await get().fetchTaskSchema(tenant, taskId, taskSchemaId);
      await useTasks.getState().fetchTask(tenant, taskId);
    } catch (error) {
      console.error('Failed to change AI agent schema visibility', error);
    }
  },
}));
