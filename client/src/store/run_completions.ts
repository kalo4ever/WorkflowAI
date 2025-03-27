import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TenantID } from '@/types/aliases';
import { LLMCompletionTypedMessages, LLMCompletionsResponse } from '@/types/workflowAI';
import { taskSubPath } from './utils';

enableMapSet();

interface RunCompletionsState {
  runCompletionsById: Map<string, Array<LLMCompletionTypedMessages>>;
  isInitializedById: Map<string, boolean>;
  isLoadingById: Map<string, boolean>;

  fetchRunCompletion(tenant: TenantID | undefined, taskId: TaskID, taskRunId: string): Promise<void>;
}

export const useRunCompletions = create<RunCompletionsState>((set, get) => ({
  runCompletionsById: new Map<string, LLMCompletionTypedMessages[]>(),
  isInitializedById: new Map<string, boolean>(),
  isLoadingById: new Map<string, boolean>(),

  fetchRunCompletion: async (tenant: TenantID | undefined, taskId: TaskID, taskRunId: string) => {
    if (get().isLoadingById.get(taskRunId)) {
      return;
    }

    set(
      produce((state: RunCompletionsState) => {
        state.isLoadingById.set(taskRunId, true);
      })
    );

    try {
      const response = await client.get<LLMCompletionsResponse>(
        taskSubPath(tenant, taskId, `/runs/${taskRunId}/completions`, true)
      );

      const completions = response.completions;

      set(
        produce((state: RunCompletionsState) => {
          state.runCompletionsById.set(taskRunId, completions);
        })
      );
    } catch (error) {
      console.error('Failed to fetch AI agent run reviews', error);
    }

    set(
      produce((state: RunCompletionsState) => {
        state.isLoadingById.set(taskRunId, false);
        state.isInitializedById.set(taskRunId, true);
      })
    );
  },
}));
