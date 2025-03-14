import { useCallback, useMemo } from 'react';
import { useRecentTasksStore } from '@/store/recentTasks';
import { rootTenantPath } from '@/store/utils';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';

export function useRecentTasksHistory(tenant: TenantID | undefined) {
  const { recentTasksByScope, addRecentTask: addRecentTaskToHistory } =
    useRecentTasksStore();

  const recentTasks = useMemo(() => {
    const scope = rootTenantPath(tenant);
    return recentTasksByScope[scope] || [];
  }, [recentTasksByScope, tenant]);

  const addRecentTask = useCallback(
    (taskId: TaskID, taskSchemaId: TaskSchemaID | undefined) => {
      addRecentTaskToHistory(tenant, taskId, taskSchemaId);
    },
    [addRecentTaskToHistory, tenant]
  );

  return {
    recentTasks,
    addRecentTask,
  };
}
