import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { PatchReviewBenchmarkRequest, ReviewBenchmark } from '@/types/workflowAI';
import { buildScopeKey, taskSchemaSubPath } from './utils';

enableMapSet();

interface ReviewBenchmarkState {
  benchmarkByScope: Map<string, ReviewBenchmark>;
  isLoadingByScope: Map<string, boolean>;
  isInitializedByScope: Map<string, boolean>;

  fetchBenchmark: (tenant: TenantID, taskId: TaskID, taskSchemaId: TaskSchemaID) => Promise<void>;

  updateBenchmark: (
    tenant: TenantID,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID,
    addVersions: number[],
    removeVersions: number[]
  ) => Promise<void>;
}

export const useReviewBenchmark = create<ReviewBenchmarkState>((set, get) => ({
  benchmarkByScope: new Map(),
  isLoadingByScope: new Map(),
  isInitializedByScope: new Map(),

  fetchBenchmark: async (tenant: TenantID, taskId: TaskID, taskSchemaId: TaskSchemaID) => {
    const scopeKey = buildScopeKey({
      tenant,
      taskId,
      taskSchemaId,
    });
    if (get().isLoadingByScope.get(scopeKey)) return;
    set(
      produce((state) => {
        state.isLoadingByScope.set(scopeKey, true);
      })
    );
    try {
      const benchmark = await client.get<ReviewBenchmark>(
        taskSchemaSubPath(tenant, taskId, taskSchemaId, '/reviews/benchmark')
      );
      set(
        produce((state) => {
          state.benchmarkByScope.set(scopeKey, benchmark);
        })
      );
    } catch (error) {
      console.error('Failed to fetch review benchmark', error);
    }
    set(
      produce((state) => {
        state.isLoadingByScope.set(scopeKey, false);
        state.isInitializedByScope.set(scopeKey, true);
      })
    );
  },

  updateBenchmark: async (
    tenant: TenantID,
    taskId: TaskID,
    taskSchemaId: TaskSchemaID,
    addVersions: number[],
    removeVersions: number[]
  ) => {
    const scopeKey = buildScopeKey({
      tenant,
      taskId,
      taskSchemaId,
    });
    try {
      const benchmark = await client.patch<PatchReviewBenchmarkRequest>(
        taskSchemaSubPath(tenant, taskId, taskSchemaId, '/reviews/benchmark'),
        {
          add_versions: addVersions,
          remove_versions: removeVersions,
        }
      );
      set(
        produce((state) => {
          state.benchmarkByScope.set(scopeKey, benchmark);
        })
      );
    } catch (error) {
      console.error('Failed to fetch review benchmark', error);
    }
  },
}));
