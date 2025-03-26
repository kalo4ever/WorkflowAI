import { ListBarTree16Regular } from '@fluentui/react-icons';
import { TaskActivityIndicator } from '@/components/TaskIterationBadge/TaskRunsActivityIndicator';
import { Loader } from '@/components/ui/Loader';
import { useOrFetchAgentsStats } from '@/store/agents';
import { isNullish } from '@/types';
import { TenantID } from '@/types/aliases';
import { SerializableTask } from '@/types/workflowAI';
import { TaskTooltip } from './TaskTooltip';

type TaskRowProps = {
  task: SerializableTask;
  onTryInPlayground: (task: SerializableTask) => void;
  onViewRuns: (task: SerializableTask) => void;
  onViewCode: (task: SerializableTask) => void;
  onViewDeployments: (task: SerializableTask) => void;
};

function RunCount(props: { runCount: number | null | undefined; isLoading: boolean }) {
  const { runCount, isLoading } = props;
  if (isLoading) {
    return <Loader size='xxsmall' />;
  }
  if (isNullish(runCount)) {
    return <div className='text-gray-700 text-base pl-2'>-</div>;
  }
  return (
    <div className='flex items-start gap-1 whitespace-nowrap'>
      <ListBarTree16Regular />
      <div>{runCount}</div>
    </div>
  );
}

const smallCostNumberFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumSignificantDigits: 4,
  maximumSignificantDigits: 4,
});

const mediumCostNumberFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

const largeCostNumberFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

function getCostFormatter(cost: number) {
  if (cost < 0.0001) {
    return smallCostNumberFormatter;
  }
  if (cost > 10) {
    return largeCostNumberFormatter;
  }
  return mediumCostNumberFormatter;
}

function Cost(props: { cost: number | null | undefined; isLoading: boolean }) {
  const { cost, isLoading } = props;
  if (isLoading) {
    return <Loader size='xxsmall' />;
  }
  if (isNullish(cost)) {
    return <div className='text-gray-700 text-base pl-2'>-</div>;
  }
  return <div>{getCostFormatter(cost).format(cost)}</div>;
}

export function TaskRow(
  props: TaskRowProps & {
    runCount: number | null | undefined;
    cost: number | null | undefined;
    isLoadingStats: boolean;
  }
) {
  const { task, onTryInPlayground, onViewRuns, onViewCode, onViewDeployments, runCount, cost, isLoadingStats } = props;

  const name = task.name.length === 0 ? task.id : task.name;

  return (
    <TaskTooltip
      onTryInPlayground={() => onTryInPlayground(task)}
      onViewRuns={() => onViewRuns(task)}
      onViewCode={() => onViewCode(task)}
      onViewDeployments={() => onViewDeployments(task)}
    >
      <div
        onClick={() => onTryInPlayground(task)}
        className='flex flex-row items-center justify-center cursor-pointer min-h-[44px] rounded-[2px] hover:bg-gray-100'
      >
        <div className='pl-2 flex-1 font-medium text-gray-900 text-[13px] items-center flex flex-row gap-1.5'>
          <TaskActivityIndicator task={task} />
          <div>{name}</div>
        </div>
        <div className='w-[100px] font-normal text-gray-500 text-[13px] max-w-[100px] overflow-hidden'>
          <RunCount runCount={runCount} isLoading={isLoadingStats} />
        </div>
        <div className='w-[57px] font-normal text-gray-500 text-[13px]'>
          <Cost cost={cost} isLoading={isLoadingStats} />
        </div>
      </div>
    </TaskTooltip>
  );
}

export function TaskRowContainer(props: TaskRowProps & { tenant: TenantID }) {
  const { tenant, ...rest } = props;
  const { isInitialized: isInitializedStats, agentsStats } = useOrFetchAgentsStats(tenant);
  const stats = agentsStats?.get(props.task.uid);

  return (
    <TaskRow
      {...rest}
      isLoadingStats={!isInitializedStats ?? false}
      runCount={stats?.run_count}
      cost={stats?.total_cost_usd}
    />
  );
}
