import { produce } from 'immer';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { rootTenantPath } from './utils';

export type RecentTasksEntry = {
  taskId: TaskID;
  taskSchemaId: TaskSchemaID | undefined;
};

interface RecentTasksStore {
  // Record instead of Map becasue Map is not correctly supported with the zustand persist
  recentTasksByScope: Record<string, RecentTasksEntry[]>;
  addRecentTask: (tenant: TenantID | undefined, taskId: TaskID, taskSchemaId: TaskSchemaID | undefined) => void;
}

export const useRecentTasksStore = create<RecentTasksStore>()(
  persist(
    (set) => ({
      recentTasksByScope: {},
      addRecentTask: (tenant, taskId, taskSchemaId) => {
        const scope = rootTenantPath(tenant);
        const MAX_ENTRIES = 7;

        const entry: RecentTasksEntry = {
          taskId,
          taskSchemaId,
        };

        set(
          produce((state) => {
            const scopeHistory = state.recentTasksByScope[scope] || [];
            const filteredScopeHistory = scopeHistory.filter(
              (historyEntry: RecentTasksEntry) => historyEntry.taskId !== taskId
            );
            state.recentTasksByScope[scope] = [entry, ...filteredScopeHistory.slice(0, MAX_ENTRIES - 1)];
          })
        );
      },
    }),
    {
      name: 'recent-tasks-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
