import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TaskSchemaID } from '@/types/aliases';
import { TenantID } from '@/types/aliases';
import { ModelResponse, Page_ModelResponse_ } from '@/types/workflowAI';
import { buildScopeKey, taskSchemaSubPath } from './utils';

enableMapSet();

interface AIModelsState {
  modelsByScope: Map<string, ModelResponse[]>;
  isLoadingByScope: Map<string, boolean>;
  isInitializedByScope: Map<string, boolean>;
  fetchModels(
    tenant: TenantID | undefined,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID
  ): Promise<void>;
}

export const useAIModels = create<AIModelsState>((set, get) => ({
  modelsByScope: new Map(),
  isLoadingByScope: new Map(),
  isInitializedByScope: new Map(),
  fetchModels: async (
    tenant: TenantID | undefined,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID
  ) => {
    if (!tenant) {
      return;
    }
    const scope = buildScopeKey({ tenant, taskId, taskSchemaId });
    if (get().isLoadingByScope.get(scope)) return;
    set({ isLoadingByScope: new Map([[scope, true]]) });
    try {
      const response = await client.get<Page_ModelResponse_>(
        taskSchemaSubPath(tenant, taskId, taskSchemaId, '/models', true)
      );
      set(
        produce((state) => {
          state.modelsByScope.set(scope, response.items);
        })
      );
    } catch (error) {
      console.error('Failed to fetch ai models', error);
    }
    set(
      produce((state) => {
        state.isLoadingByScope.set(scope, false);
        state.isInitializedByScope.set(scope, true);
      })
    );
  },
}));
