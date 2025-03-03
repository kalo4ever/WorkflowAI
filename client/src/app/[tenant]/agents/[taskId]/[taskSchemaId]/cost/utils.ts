import { TaskStats } from '@/types/workflowAI';

export enum TimeFrame {
  YESTERDAY = 'Yesterday',
  LAST_WEEK = 'Last Week',
  LAST_MONTH = 'Last Month',
  LAST_YEAR = 'Last Year',
  ALL_TIME = 'All Time',
}

export function getTimeFrameStartDate(timeFrame: TimeFrame): Date {
  const now = new Date();
  let startDate: Date;
  switch (timeFrame) {
    case TimeFrame.YESTERDAY:
      startDate = new Date(now.setDate(now.getDate() - 1));
      break;
    case TimeFrame.LAST_WEEK:
      startDate = new Date(now.setDate(now.getDate() - 7));
      break;
    case TimeFrame.LAST_MONTH:
      startDate = new Date(now.setDate(now.getDate() - 30));
      break;
    case TimeFrame.LAST_YEAR:
      startDate = new Date(now.setDate(now.getDate() - 365));
      break;
    case TimeFrame.ALL_TIME:
      startDate = new Date(0);
      break;
  }
  return startDate;
}

type CostDataEntry = {
  x: string;
  y: number;
};

type CostData = {
  data: CostDataEntry[];
  total: number;
};

export function processTaskStats(
  taskStats: TaskStats[],
  mode: 'cost' | 'runs',
  timeFrame: TimeFrame
): CostData {
  const statsMap = new Map(
    taskStats.map((stats) => [
      new Date(stats.date).toISOString().split('T')[0],
      stats,
    ])
  );

  let startDate: Date;

  if (timeFrame === TimeFrame.ALL_TIME && taskStats.length > 0) {
    startDate = new Date(
      Math.min(...taskStats.map((stats) => new Date(stats.date).getTime()))
    );
  } else {
    startDate = getTimeFrameStartDate(timeFrame);
  }

  const data: CostDataEntry[] = [];
  const endDate = new Date();
  let total = 0;

  for (
    let date = new Date(startDate);
    date <= endDate;
    date.setDate(date.getDate() + 1)
  ) {
    const formattedDate = `${date.getMonth() + 1}/${date.getDate()}`;
    const dateKey = date.toISOString().split('T')[0];
    const stats = statsMap.get(dateKey);

    let value = 0;
    if (stats) {
      value = mode === 'cost' ? stats.total_cost_usd : stats.total_count;
      total += value;
    }

    data.push({ x: formattedDate, y: value });
  }

  return { data, total };
}
