import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { SearchFields } from '@/types/workflowAI';
import { buildScopeKey, taskSchemaSubPath } from './utils';

enableMapSet();

interface TaskRunsSearchFieldsState {
  searchFieldsByScope: Map<string, SearchFields>;
  isInitializedByScope: Map<string, boolean>;
  isLoadingByScope: Map<string, boolean>;

  fetchSearchFields(params: {
    tenant: TenantID | undefined;
    taskId: TaskID;
    taskSchemaId: TaskSchemaID;
  }): Promise<undefined>;
}

export const useTaskRunsSearchFields = create<TaskRunsSearchFieldsState>(
  (set, get) => ({
    searchFieldsByScope: new Map<string, SearchFields>(),
    isInitializedByScope: new Map<string, boolean>(),
    isLoadingByScope: new Map<string, boolean>(),

    fetchSearchFields: async ({ tenant, taskId, taskSchemaId }) => {
      const scope = buildScopeKey({
        tenant,
        taskId,
        taskSchemaId,
      });
      if (get().isLoadingByScope.get(scope)) {
        return;
      }
      set(
        produce((state: TaskRunsSearchFieldsState) => {
          state.isLoadingByScope.set(scope, true);
        })
      );

      try {
        const searchFields = await client.get<SearchFields>(
          taskSchemaSubPath(
            tenant,
            taskId,
            taskSchemaId,
            `/runs/search/fields`,
            true
          )
        );

        set(
          produce((state) => {
            state.searchFieldsByScope.set(scope, searchFields);
          })
        );
      } catch (error) {
        console.error('Failed to fetch AI agents runs search fields', error);
      }
      set(
        produce((state: TaskRunsSearchFieldsState) => {
          state.isInitializedByScope.set(scope, true);
          state.isLoadingByScope.set(scope, false);
        })
      );
    },
  })
);
