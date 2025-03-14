import { captureException } from '@sentry/nextjs';
import { produce } from 'immer';
import { useCallback, useEffect } from 'react';
import { create } from 'zustand';
import { client } from '@/lib/api';
import { LeaderboardTaskEntry } from '@/types/leaderboard';
import { ReviewBenchmark, SerializableTask } from '@/types/workflowAI';
import { rootTaskPath, taskSchemaSubPath } from './utils';

export type LeaderboardTaskData = {
  readonly task: SerializableTask;
  readonly benchmark: ReviewBenchmark;
};

export function leaderboardScope({
  tenantId,
  taskId,
  schemaId,
}: LeaderboardTaskEntry) {
  return `${tenantId}/${taskId}/${schemaId}`;
}

async function fetchTaskData({
  tenantId,
  taskId,
  schemaId,
}: LeaderboardTaskEntry): Promise<LeaderboardTaskData> {
  const task = await client.get<SerializableTask>(
    `${rootTaskPath(tenantId)}/${taskId}`
  );

  const benchmark = await client.get<ReviewBenchmark>(
    `${taskSchemaSubPath(tenantId, taskId, schemaId, '/reviews/benchmark')}`
  );

  return { task, benchmark };
}

interface LeaderboardState {
  leaderboard: Map<string, LeaderboardTaskData>;
  isLoading: Map<string, boolean>;
  // Not setting the initialized here as when initialized it should just
  // be present in the leaderboard (all data should exist)
  fetchLeaderboard(entry: LeaderboardTaskEntry): Promise<void>;
}

export const useLeaderboardStore = create<LeaderboardState>((set, get) => ({
  leaderboard: new Map(),
  isLoading: new Map(),
  fetchLeaderboard: async (entry) => {
    const scope = leaderboardScope(entry);
    if (get().isLoading.get(scope)) return;
    set(
      produce((state) => {
        state.isLoading.set(scope, true);
      })
    );
    try {
      const { task, benchmark } = await fetchTaskData(entry);
      set(
        produce((state) => {
          state.leaderboard.set(scope, { task, benchmark });
        })
      );
    } catch (error) {
      captureException(error);
      console.error('Failed to fetch leaderboard', error);
    } finally {
      set(
        produce((state) => {
          state.isLoading.set(scope, false);
        })
      );
    }
  },
}));

export function useLeaderboard(entries: readonly LeaderboardTaskEntry[]) {
  const leaderboard = useLeaderboardStore((state) => state.leaderboard);
  const isLoading = useLeaderboardStore((state) => state.isLoading);
  const fetchLeaderboard = useLeaderboardStore(
    (state) => state.fetchLeaderboard
  );

  useEffect(() => {
    for (const entry of entries) {
      if (!leaderboard.has(leaderboardScope(entry))) {
        fetchLeaderboard(entry);
      }
    }
  }, [fetchLeaderboard, entries, leaderboard]);

  const leaderboardByEntry = useCallback(
    (entry: LeaderboardTaskEntry) => {
      return leaderboard.get(leaderboardScope(entry));
    },
    [leaderboard]
  );

  const isLoadingByEntry = useCallback(
    (entry: LeaderboardTaskEntry) => {
      return isLoading.get(leaderboardScope(entry));
    },
    [isLoading]
  );

  return { leaderboard, leaderboardByEntry, isLoadingByEntry };
}
