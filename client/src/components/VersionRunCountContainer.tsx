import { useOrFetchVersionsStats } from '@/store/versions';
import { TaskID, TenantID } from '@/types/aliases';
import { TaskRunCountButton } from './v2/TaskRunCountBadge/TaskRunCountBadge';

export function VersionRunCountContainer(props: {
  onClick?: (() => void) | undefined;
  tenant: TenantID;
  taskId: TaskID;
  version_id: string;
}) {
  const { tenant, taskId, version_id } = props;
  const { isInitialized, versionsStats } = useOrFetchVersionsStats(tenant, taskId);

  const runsCount = versionsStats?.get(version_id)?.run_count;

  return <TaskRunCountButton {...props} runsCount={runsCount} isLoading={!isInitialized} />;
}
