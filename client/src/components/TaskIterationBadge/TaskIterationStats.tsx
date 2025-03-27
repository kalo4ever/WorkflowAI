import { Loader2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useIsMounted } from 'usehooks-ts';
import { useTaskStats } from '@/store/task_stats';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';

type TaskStatsProps = {
  tenant: TenantID | undefined;
  taskSchemaId: TaskSchemaID;
  taskId: TaskID;
  iteration?: number;
};

export function TaskStats(props: TaskStatsProps) {
  const { tenant, taskSchemaId, taskId, iteration } = props;

  const fetchTaskStats = useTaskStats((state) => state.fetchTaskStats);

  const [totalCount, setTotalCount] = useState<number | undefined>(undefined);

  const isMounted = useIsMounted();

  useEffect(() => {
    const fortyEightHoursAgo = new Date(Date.now() - 48 * 60 * 60 * 1000);

    async function fetchStats() {
      if (!isMounted()) return;

      const stats = await fetchTaskStats(tenant, taskId, fortyEightHoursAgo, undefined, taskSchemaId, iteration, true);

      if (!stats) {
        return;
      }

      let totalCount = 0;
      stats.forEach((stat) => {
        totalCount += stat.total_count;
      });

      setTotalCount(totalCount);
    }

    fetchStats();
  }, [fetchTaskStats, taskId, taskSchemaId, iteration, tenant, isMounted]);

  const text = useMemo(() => {
    if (totalCount === undefined) {
      return undefined;
    }

    switch (totalCount) {
      case 1:
        return `Active: 1 run today and yesterday`;
      default:
        return `Active: ${totalCount} runs today and yesterday`;
    }
  }, [totalCount]);

  if (text === undefined) {
    return <Loader2 className='h-4 w-4 animate-spin text-gray-400' />;
  }

  return <div>{text}</div>;
}
