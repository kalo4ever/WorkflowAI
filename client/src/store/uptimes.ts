import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { client } from '@/lib/api';

enableMapSet();

interface UptimesState {
  workflowUptime: number | undefined;
  openaiUptime: number | undefined;
  isLoadingOpenaiUptime: boolean;
  isLoadingWorkflowaiUptime: boolean;
  isInitializedOpenaiUptime: boolean;
  isInitializedWorkflowaiUptime: boolean;

  fetchWorkflowaiUptime(): Promise<void>;
  fetchOpenaiUptime(): Promise<void>;
}

export const useUptimes = create<UptimesState>((set, get) => ({
  workflowUptime: undefined,
  openaiUptime: undefined,
  isLoadingOpenaiUptime: false,
  isLoadingWorkflowaiUptime: false,
  isInitializedOpenaiUptime: false,
  isInitializedWorkflowaiUptime: false,

  fetchWorkflowaiUptime: async () => {
    if (get().isLoadingWorkflowaiUptime) return;

    set(
      produce((state) => {
        state.isLoadingWorkflowaiUptime = true;
      })
    );

    const path = `/api/data/features/uptimes/workflowai`;

    try {
      const response = await client.get<{ uptime_percent: number }>(path);
      set(
        produce((state) => {
          state.workflowUptime = response.uptime_percent;
        })
      );
    } catch (error) {
      console.error('Failed to fetch workflowai uptime', error);
    } finally {
      set(
        produce((state) => {
          state.isLoadingWorkflowaiUptime = false;
          state.isInitializedWorkflowaiUptime = true;
        })
      );
    }
  },

  fetchOpenaiUptime: async () => {
    if (get().isLoadingOpenaiUptime) return;

    set(
      produce((state) => {
        state.isLoadingOpenaiUptime = true;
      })
    );

    const path = `/api/data/features/uptimes/openai`;

    try {
      const response = await client.get<{ uptime_percent: number }>(path);
      set(
        produce((state) => {
          state.openaiUptime = response.uptime_percent;
        })
      );
    } catch (error) {
      console.error('Failed to fetch openai uptime', error);
    } finally {
      set(
        produce((state) => {
          state.isLoadingOpenaiUptime = false;
          state.isInitializedOpenaiUptime = true;
        })
      );
    }
  },
}));
