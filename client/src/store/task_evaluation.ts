import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import {
  InputEvaluationData,
  InputEvaluationPatchRequest,
  Page_InputEvaluationData_,
  TaskEvaluationPatchRequest,
  TaskEvaluationResponse,
} from '@/types/workflowAI';
import { buildScopeKey, taskSchemaSubPath } from './utils';

enableMapSet();

interface TaskEvaluationState {
  evaluationInputsByScope: Map<string, InputEvaluationData[]>;
  isLoadingEvaluationInputsByScope: Map<string, boolean>;
  isInitializedEvaluationInputsByScope: Map<string, boolean>;

  evaluationByScope: Map<string, TaskEvaluationResponse>;
  isLoadingEvaluationByScope: Map<string, boolean>;
  isInitializedEvaluationByScope: Map<string, boolean>;

  fetchEvaluationInputs: (tenant: TenantID | undefined, taskId: TaskID, taskSchemaId: TaskSchemaID) => Promise<void>;

  fetchEvaluation: (tenant: TenantID | undefined, taskId: TaskID, taskSchemaId: TaskSchemaID) => Promise<void>;

  updateEvaluation: (
    tenant: TenantID | undefined,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID,
    instructions: string
  ) => void;

  updateEvaluationInputs: (
    tenant: TenantID | undefined,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID,
    taskInputHash: string,
    request: InputEvaluationPatchRequest
  ) => void;
}

export const useTaskEvaluation = create<TaskEvaluationState>((set, get) => ({
  evaluationInputsByScope: new Map(),
  isLoadingEvaluationInputsByScope: new Map(),
  isInitializedEvaluationInputsByScope: new Map(),

  evaluationByScope: new Map(),
  isLoadingEvaluationByScope: new Map(),
  isInitializedEvaluationByScope: new Map(),

  fetchEvaluationInputs: async (tenant, taskId, taskSchemaId) => {
    const scopeKey = buildScopeKey({
      tenant,
      taskId,
      taskSchemaId,
    });

    if (get().isLoadingEvaluationInputsByScope.get(scopeKey)) return;
    set(
      produce((state) => {
        state.isLoadingEvaluationInputsByScope.set(scopeKey, true);
      })
    );

    const path = taskSchemaSubPath(tenant, taskId, taskSchemaId, '/evaluation/inputs');

    try {
      const { items } = await client.get<Page_InputEvaluationData_>(path);

      set(
        produce((state) => {
          state.evaluationInputsByScope.set(scopeKey, items);
        })
      );
    } catch (error) {
      console.error('Failed to fetch evaluation inputs', error);
    }

    set(
      produce((state) => {
        state.isLoadingEvaluationInputsByScope.set(scopeKey, false);
        state.isInitializedEvaluationInputsByScope.set(scopeKey, true);
      })
    );
  },

  fetchEvaluation: async (tenant, taskId, taskSchemaId) => {
    const scopeKey = buildScopeKey({
      tenant,
      taskId,
      taskSchemaId,
    });

    if (get().isLoadingEvaluationByScope.get(scopeKey)) return;
    set(
      produce((state) => {
        state.isLoadingEvaluationByScope.set(scopeKey, true);
      })
    );

    const path = taskSchemaSubPath(tenant, taskId, taskSchemaId, '/evaluation');

    try {
      const response = await client.get<TaskEvaluationResponse>(path);

      set(
        produce((state) => {
          state.evaluationByScope.set(scopeKey, response);
        })
      );
    } catch (error) {
      console.error('Failed to fetch evaluation', error);
    }

    set(
      produce((state) => {
        state.isLoadingEvaluationByScope.set(scopeKey, false);
        state.isInitializedEvaluationByScope.set(scopeKey, true);
      })
    );
  },

  updateEvaluation: async (tenant, taskId, taskSchemaId, instructions) => {
    const scopeKey = buildScopeKey({ tenant, taskId, taskSchemaId });

    const path = taskSchemaSubPath(tenant, taskId, taskSchemaId, '/evaluation');

    try {
      const response = await client.patch<TaskEvaluationPatchRequest>(path, {
        evaluation_instructions: instructions,
      });

      set(
        produce((state) => {
          state.evaluationByScope.set(scopeKey, response);
        })
      );
    } catch (error) {
      console.error('Failed to patch evaluation', error);
    }
  },

  updateEvaluationInputs: async (tenant, taskId, taskSchemaId, taskInputHash, request) => {
    const path = taskSchemaSubPath(tenant, taskId, taskSchemaId, `/evaluation/inputs/${taskInputHash}`);

    try {
      await client.patch<InputEvaluationPatchRequest, InputEvaluationData>(path, request);
    } catch (error) {
      console.error('Failed to patch evaluation inputs', error);
    }

    await get().fetchEvaluationInputs(tenant, taskId, taskSchemaId);
    await get().fetchEvaluation(tenant, taskId, taskSchemaId);
  },
}));
