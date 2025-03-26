'use client';

import { useCallback, useMemo } from 'react';
import { BarChart } from '@/components/ui/BarChart';
import { Loader } from '@/components/ui/Loader';
import { PageContainer } from '@/components/v2/PageContainer';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { useParsedSearchParams, useRedirectWithParams } from '@/lib/queryString';
import { useOrFetchTask, useOrFetchTaskStats } from '@/store/fetchers';
import { CostChartHeader } from './CostChartHeader';
import { CostPopover } from './CostPopover';
import { TimeFrame, getTimeFrameStartDate, processTaskStats } from './utils';

export function CostContainer() {
  const { taskId, tenant } = useTaskSchemaParams();

  const { task, isInitialized: isTaskInitialized } = useOrFetchTask(tenant, taskId);

  const storedTimeFrame = useMemo(() => {
    return localStorage.getItem('timeFrame') as TimeFrame | undefined;
  }, []);

  const { timeFrame: timeFrameValue } = useParsedSearchParams('timeFrame');
  const timeFrame = (timeFrameValue as TimeFrame) ?? storedTimeFrame ?? TimeFrame.LAST_MONTH;

  const redirectWithParams = useRedirectWithParams();
  const onTimeFrameChange = useCallback(
    (timeFrame: TimeFrame) => {
      localStorage.setItem('timeFrame', timeFrame);
      redirectWithParams({
        params: { timeFrame: timeFrame },
      });
    },
    [redirectWithParams]
  );

  const startDate = useMemo(() => {
    return getTimeFrameStartDate(timeFrame);
  }, [timeFrame]);

  const { taskStats, isInitialized: isTaskStatsInitialized } = useOrFetchTaskStats(tenant, taskId, startDate);

  const { data: costData, total: costTotal } = useMemo(() => {
    return processTaskStats(taskStats ?? [], 'cost', timeFrame);
  }, [taskStats, timeFrame]);

  const { data: runsData, total: runsTotal } = useMemo(() => {
    return processTaskStats(taskStats ?? [], 'runs', timeFrame);
  }, [taskStats, timeFrame]);

  const isLargeChunkOfTime =
    timeFrame === TimeFrame.LAST_MONTH || timeFrame === TimeFrame.LAST_YEAR || timeFrame === TimeFrame.ALL_TIME;

  const showValueAboveBar = !isLargeChunkOfTime;
  const showTooltips = isLargeChunkOfTime;

  return (
    <PageContainer
      task={task}
      isInitialized={isTaskInitialized}
      name='Cost'
      showCopyLink={true}
      showBottomBorder={false}
      showSchema={false}
    >
      <div className='flex flex-col h-full w-full'>
        <div className='flex flex-row w-full pb-3 pl-4 border-b border-dashed border-gray-200'>
          <CostPopover timeFrame={timeFrame} onTimeFrameChange={onTimeFrameChange} />
        </div>

        {!isTaskStatsInitialized ? (
          <Loader centered />
        ) : (
          <div className='flex flex-col h-full w-full gap-10 overflow-auto'>
            <div className='flex flex-col gap-2'>
              <CostChartHeader
                headerText='Cost per Day Across All Schemas'
                topText={`${timeFrame} Total`}
                bottomText={`$${costTotal.toFixed(2)}`}
              />
              <BarChart
                data={costData}
                fractionalPart={2}
                prefix='$'
                barColor='#818CF8'
                textColor='#6B7280'
                showValueAboveBar={showValueAboveBar}
                showTooltips={showTooltips}
                barRadius={2}
                tooltipLabel='Cost'
                className='pr-4'
              />
            </div>
            <div className='flex flex-col gap-2'>
              <CostChartHeader
                headerText='Runs per Day Across All Schemas'
                topText={`${timeFrame} Total`}
                bottomText={`${runsTotal}`}
                showTopBorder={true}
              />
              <BarChart
                data={runsData}
                fractionalPart={0}
                className='mb-10 pr-4'
                barColor='#818CF8'
                textColor='#6B7280'
                showValueAboveBar={showValueAboveBar}
                showTooltips={showTooltips}
                barRadius={2}
                hideFractionsOnYAxis={true}
                tooltipLabel='Runs'
              />
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}

{
  /* <div className='flex flex-row w-fit mb-5'>
  <CostPopover timeFrame={timeFrame} onTimeFrameChange={onTimeFrameChange} />
</div>; */
}
