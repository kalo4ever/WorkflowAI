import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { SearchFieldParam } from '@/lib/routeFormatter';
import { taskRunsRoute } from '@/lib/routeFormatter';
import { TaskSchemaID } from '@/types/aliases';

export function useViewRuns(
  taskSchemaId: TaskSchemaID | number | undefined,
  version?: { id: string; semver?: unknown[] | null }
) {
  const router = useRouter();
  const { tenant, taskId } = useTaskSchemaParams();

  return useCallback(() => {
    if (!taskSchemaId || !version) return;
    const version_id = version.semver ? version.semver.join('.') : version.id;
    router.push(
      taskRunsRoute(tenant, taskId, taskSchemaId as TaskSchemaID, {
        [SearchFieldParam.FieldNames]: 'schema,version',
        [SearchFieldParam.Operators]: 'is,is',
        [SearchFieldParam.Values]: `${taskSchemaId},${version_id}`,
      })
    );
  }, [taskSchemaId, version, router, tenant, taskId]);
}
