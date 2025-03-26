import { enableMapSet, produce } from 'immer';
import { useEffect } from 'react';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { Page } from '@/types';
import { TaskID, TenantID } from '@/types/aliases';
import { FeedbackItem } from '@/types/workflowAI';
import { buildScopeKey, taskSubPath } from './utils';

enableMapSet();

interface FeedbackState {
  feedbackByScope: Map<string, FeedbackItem[]>;
  isFeedbackLoadingByScope: Map<string, boolean>;
  isFeedbackInitializedByScope: Map<string, boolean>;
  fetchFeedback(tenant: TenantID, taskId: TaskID, runId?: string): Promise<void>;
}

export const useFeedback = create<FeedbackState>((set, get) => ({
  feedbackByScope: new Map<string, FeedbackItem[]>(),
  isFeedbackLoadingByScope: new Map<string, boolean>(),
  isFeedbackInitializedByScope: new Map<string, boolean>(),
  fetchFeedback: async (tenant, taskId, runId) => {
    const scope = buildScopeKey({ tenant, taskId, searchParams: runId });
    if (get().isFeedbackInitializedByScope.get(scope)) return;
    set(
      produce<FeedbackState>((state) => {
        state.isFeedbackLoadingByScope.set(scope, true);
      })
    );
    try {
      const path = runId ? `/runs/${runId}/feedback` : '/feedback';
      const url = taskSubPath(tenant, taskId, path, true);
      const feedback = await client.get<Page<FeedbackItem>>(url);
      set(
        produce<FeedbackState>((state) => {
          state.feedbackByScope.set(scope, feedback.items);
          state.isFeedbackLoadingByScope.set(scope, false);
          state.isFeedbackInitializedByScope.set(scope, true);
        })
      );
    } catch (error) {
      set(
        produce<FeedbackState>((state) => {
          state.isFeedbackLoadingByScope.set(scope, false);
          state.isFeedbackInitializedByScope.set(scope, true);
        })
      );
    }
  },
}));

export function useOrFetchFeedback(tenant: TenantID | undefined, taskId: TaskID, runId?: string) {
  const scope = buildScopeKey({ tenant, taskId, searchParams: runId });
  const feedbackList = useFeedback((state) => state.feedbackByScope.get(scope));

  const isLoading = useFeedback((state) => state.isFeedbackLoadingByScope.get(scope));

  const isInitialized = useFeedback((state) => state.isFeedbackInitializedByScope.get(scope));

  const fetchFeedback = useFeedback((state) => state.fetchFeedback);

  useEffect(() => {
    if (tenant && taskId && !isInitialized && !isLoading) {
      fetchFeedback(tenant, taskId, runId);
    }
  }, [fetchFeedback, tenant, taskId, isInitialized, isLoading, runId]);

  return {
    feedbackList,
    isLoading,
    isInitialized,
  };
}
